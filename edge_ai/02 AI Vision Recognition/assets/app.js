// SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
//
// SPDX-License-Identifier: MPL-2.0

const statusDot = document.getElementById('status-dot');
const statusLabel = document.getElementById('status-label');
const statusText = document.getElementById('status-text');
const errorContainer = document.getElementById('error-container');
const iframe = document.getElementById('camera-stream');
const placeholder = document.getElementById('video-placeholder');
const detectionsList = document.getElementById('detections-list');

const socket = io(`http://${window.location.host}`);
const streamUrl = `http://${window.location.hostname}:4912/embed`;

let reloadTimer;
let streamLoaded = false;
let currentDetections = [];

// ── Object icons ──────────────────────────────────────────

const objectIcons = {
    'cup': '☕',
    'person': '🧑',
    'cell phone': '📱',
    'bottle': '🍾',
    'book': '📖',
    'chair': '🪑',
    'laptop': '💻',
    'mouse': '🖱️',
    'keyboard': '⌨️',
    'clock': '⏰',
    'default': '📦',
};

function getIcon(name) {
    return objectIcons[name] || objectIcons['default'];
}

// ── Stream ────────────────────────────────────────────────

function setStatus(state, label) {
    statusDot.className = `status-indicator ${state}`;
    statusLabel.textContent = label;
}

function loadStream() {
    if (!streamLoaded) {
        iframe.src = streamUrl;
    }
}

iframe.addEventListener('load', () => {
    streamLoaded = true;
    clearInterval(reloadTimer);
    placeholder.style.display = 'none';
    iframe.style.display = 'block';
    setStatus('on', 'Connected');
    statusText.textContent = 'AI detecting objects in real time';
});

// ── Detections ────────────────────────────────────────────

function renderDetections(objects) {
    if (!objects || objects.length === 0) {
        detectionsList.innerHTML = `
            <div class="no-detections">
                <p>Point the camera at a cup, person, or cell phone</p>
            </div>`;
        return;
    }

    let html = '';
    objects.forEach(obj => {
        html += `
            <div class="detection-item">
                <div class="detection-icon">${getIcon(obj.object)}</div>
                <div class="detection-info">
                    <div class="detection-name">${obj.object}</div>
                    <div class="detection-confidence">${obj.confidence}%</div>
                    <div class="detection-bar">
                        <div class="detection-bar-fill" style="width: ${obj.confidence}%"></div>
                    </div>
                </div>
            </div>`;
    });
    detectionsList.innerHTML = html;
}

// ── Socket ────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    setStatus('', 'Connecting');
    loadStream();
    reloadTimer = setInterval(loadStream, 1000);
});

socket.on('connect', () => {
    errorContainer.style.display = 'none';
    errorContainer.textContent = '';
});

socket.on('detections', (data) => {
    if (data && data.objects) {
        renderDetections(data.objects);
    }
});

socket.on('disconnect', () => {
    setStatus('error', 'Disconnected');
    statusText.textContent = 'Detection unavailable';
    errorContainer.textContent = 'Connection lost. Check the board and try again.';
    errorContainer.style.display = 'block';
});
