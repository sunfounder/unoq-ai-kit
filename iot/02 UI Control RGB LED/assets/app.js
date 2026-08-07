// SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
//
// SPDX-License-Identifier: MPL-2.0

const wheel = document.getElementById('color-wheel');
const wheelCtx = wheel.getContext('2d');
const indicator = document.getElementById('wheel-indicator');
const brightnessSlider = document.getElementById('brightness-slider');
const rgbValues = document.getElementById('rgb-values');
const hexValue = document.getElementById('hex-value');
const statusDot = document.getElementById('status-dot');
const statusLabel = document.getElementById('status-label');
const statusText = document.getElementById('status-text');
const errorContainer = document.getElementById('error-container');

const socket = io(`http://${window.location.host}`);

// ── State ─────────────────────────────────────────────────

const RADIUS = 120;          // wheel radius (canvas is 240×240)
const CENTER = RADIUS;
let wheelImage = null;       // cached wheel image
let hue = 0;                 // 0–360
let saturation = 0;          // 0–1
let brightness = 100;        // 0–100
let isDragging = false;
let lastSent = { r: -1, g: -1, b: -1 };  // dedupe sends

// ── HSV → RGB ─────────────────────────────────────────────

function hsvToRgb(h, s, v) {
    // h: 0-360, s: 0-1, v: 0-1
    const f = (h % 360) / 60;
    const i = Math.floor(f) % 6;
    const p = v * (1 - s);
    const q = v * (1 - (f - i) * s);
    const t = v * (1 - (1 - (f - i)) * s);
    let r, g, b;
    switch (i) {
        case 0: r = v; g = t; b = p; break;
        case 1: r = q; g = v; b = p; break;
        case 2: r = p; g = v; b = t; break;
        case 3: r = p; g = q; b = v; break;
        case 4: r = t; g = p; b = v; break;
        case 5: r = v; g = p; b = q; break;
    }
    return {
        r: Math.round(r * 255),
        g: Math.round(g * 255),
        b: Math.round(b * 255),
    };
}

function rgbToHex(r, g, b) {
    return '#' + [r, g, b].map(c => c.toString(16).padStart(2, '0')).join('');
}

// ── Draw color wheel (once, then cached) ──────────────────

function drawWheel() {
    const size = RADIUS * 2;
    const imageData = wheelCtx.createImageData(size, size);
    const data = imageData.data;

    for (let py = 0; py < size; py++) {
        for (let px = 0; px < size; px++) {
            const dx = px - CENTER;
            const dy = py - CENTER;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist > RADIUS) continue;  // outside circle → transparent

            const h = (Math.atan2(dy, dx) * 180 / Math.PI + 360) % 360;
            const s = Math.min(dist / RADIUS, 1);
            const { r, g, b } = hsvToRgb(h, s, 1);

            const idx = (py * size + px) * 4;
            data[idx]     = r;
            data[idx + 1] = g;
            data[idx + 2] = b;
            data[idx + 3] = 255;
        }
    }

    wheelCtx.putImageData(imageData, 0, 0);
    wheelImage = wheelCtx.getImageData(0, 0, size, size);
}

// ── Move indicator to position ────────────────────────────

function moveIndicator(h, s) {
    const angle = h * Math.PI / 180;
    const dist = s * RADIUS;
    const x = CENTER + dist * Math.cos(angle);
    const y = CENTER + dist * Math.sin(angle);
    indicator.style.left = x + 'px';
    indicator.style.top = y + 'px';
}

// ── Get current RGB (applying brightness) ─────────────────

function getCurrentRgb() {
    // saturation is always 1 at wheel edge, 0 at center
    // But when hue=0, sat=0 (center), we treat it as off
    const effectiveSat = (hue === 0 && saturation < 0.01) ? 0 : saturation;
    return hsvToRgb(hue, effectiveSat, brightness / 100);
}

// ── Update UI display ─────────────────────────────────────

function updateDisplay(r, g, b) {
    const hex = rgbToHex(r, g, b);
    rgbValues.textContent = 'R: ' + r + '    G: ' + g + '    B: ' + b;
    hexValue.textContent = hex;

    // Update brightness slider track color
    const hueColor = hsvToRgb(hue, 1, 1);
    const hueHex = rgbToHex(hueColor.r, hueColor.g, hueColor.b);
    brightnessSlider.style.background =
        'linear-gradient(to right, #000, ' + hueHex + ')';
}

// ── Send color to server (deduped) ────────────────────────

function sendColor(r, g, b) {
    if (r === lastSent.r && g === lastSent.g && b === lastSent.b) return;
    lastSent = { r, g, b };
    socket.emit('set_rgb_color', { r, g, b });
}

// ── Handle wheel interaction ──────────────────────────────

function getPosFromEvent(e) {
    const rect = wheel.getBoundingClientRect();
    const scaleX = wheel.width / rect.width;   // account for CSS scaling
    const scaleY = wheel.height / rect.height;
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return {
        x: (clientX - rect.left) * scaleX,
        y: (clientY - rect.top) * scaleY,
    };
}

function updateFromPos(pos) {
    const dx = pos.x - CENTER;
    const dy = pos.y - CENTER;
    const dist = Math.sqrt(dx * dx + dy * dy);

    hue = (Math.atan2(dy, dx) * 180 / Math.PI + 360) % 360;
    saturation = Math.min(dist / RADIUS, 1);

    moveIndicator(hue, saturation);

    const { r, g, b } = getCurrentRgb();
    updateDisplay(r, g, b);
    sendColor(r, g, b);
}

function onWheelStart(e) {
    isDragging = true;
    indicator.classList.add('active');
    updateFromPos(getPosFromEvent(e));
    e.preventDefault();
}

function onWheelMove(e) {
    if (!isDragging) return;
    updateFromPos(getPosFromEvent(e));
    e.preventDefault();
}

function onWheelEnd(e) {
    if (!isDragging) return;
    isDragging = false;
    indicator.classList.remove('active');
    e.preventDefault();
}

// ── Brightness slider ─────────────────────────────────────

function onBrightnessChange() {
    brightness = parseInt(brightnessSlider.value);
    const { r, g, b } = getCurrentRgb();
    updateDisplay(r, g, b);
    sendColor(r, g, b);
}

// ── Default UI ────────────────────────────────────────────

function setDefaultUI() {
    hue = 0;
    saturation = 0;
    brightness = 100;
    brightnessSlider.value = 100;
    moveIndicator(0, 0);
    updateDisplay(0, 0, 0);
    statusDot.className = 'status-indicator';
    statusLabel.textContent = 'Ready';
    statusText.textContent = 'Drag the color wheel to control the RGB LED';
    errorContainer.style.display = 'none';
}

// ── Socket ────────────────────────────────────────────────

function setStatus(state) {
    statusDot.className = 'status-indicator ' + state;
    if (state === 'on') {
        statusLabel.textContent = 'Connected';
    } else if (state === 'error') {
        statusLabel.textContent = 'Disconnected';
    } else {
        statusLabel.textContent = 'Ready';
    }
}

function initSocketIO() {
    socket.on('connect', () => {
        socket.emit('get_initial_state', {});
        setStatus('on');
        errorContainer.style.display = 'none';
        errorContainer.textContent = '';
    });

    socket.on('rgb_status_update', (data) => {
        // Update from server state
        const r = data.r, g = data.g, b = data.b;
        updateDisplay(r, g, b);
        lastSent = { r, g, b };
    });

    socket.on('disconnect', () => {
        setStatus('error');
        errorContainer.textContent = 'Connection lost. Check your board and try again.';
        errorContainer.style.display = 'block';
    });
}

// ── Init ──────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    drawWheel();
    setDefaultUI();
    initSocketIO();

    // Mouse events
    wheel.addEventListener('mousedown', onWheelStart);
    document.addEventListener('mousemove', onWheelMove);
    document.addEventListener('mouseup', onWheelEnd);

    // Touch events
    wheel.addEventListener('touchstart', onWheelStart, { passive: false });
    document.addEventListener('touchmove', onWheelMove, { passive: false });
    document.addEventListener('touchend', onWheelEnd);

    // Brightness
    brightnessSlider.addEventListener('input', onBrightnessChange);
});
