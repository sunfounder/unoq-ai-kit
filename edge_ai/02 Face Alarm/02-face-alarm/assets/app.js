// SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
//
// SPDX-License-Identifier: MPL-2.0

const socket = io(`http://${window.location.host}`);

const statusDot = document.getElementById('status-dot');
const statusLabel = document.getElementById('status-label');
const faceStatus = document.getElementById('face-status');
const statusText = document.getElementById('status-text');
const errorContainer = document.getElementById('error-container');
const iframe = document.getElementById('camera-stream');

const streamUrl = `http://${window.location.hostname}:4912/embed`;
let streamLoaded = false;

// ── Camera stream ─────────────────────────────────────────

function loadStream() {
    if (!streamLoaded) {
        iframe.src = streamUrl;
    }
}

iframe.addEventListener('load', () => {
    streamLoaded = true;
    iframe.style.display = 'block';
});

// ── Socket ────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    loadStream();
    setInterval(loadStream, 1000);
});

socket.on('connect', () => {
    statusDot.className = 'status-indicator on';
    statusLabel.textContent = 'Connected';
    errorContainer.style.display = 'none';
});

socket.on('disconnect', () => {
    statusDot.className = 'status-indicator error';
    statusLabel.textContent = 'Disconnected';
    errorContainer.textContent = 'Connection lost. Check the board.';
    errorContainer.style.display = 'block';
});

socket.on('face_status', (msg) => {
    const detected = Boolean(msg.detected);

    faceStatus.textContent = detected
        ? '🚨 Face detected — Alarm ON'
        : 'No face — Alarm OFF';

    faceStatus.classList.toggle('detected', detected);

    statusText.textContent = detected
        ? 'The buzzer is sounding!'
        : 'Show your face to trigger the alarm';
});
