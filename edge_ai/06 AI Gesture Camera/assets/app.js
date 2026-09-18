// SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
//
// SPDX-License-Identifier: MPL-2.0

const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const currentGesture = document.getElementById('current-gesture');
const gestureConfidence = document.getElementById('gesture-confidence');
const lastAction = document.getElementById('last-action');
const cameraStream = document.getElementById('camera-stream');
const videoPlaceholder = document.getElementById('video-placeholder');

const socket = io(`http://${window.location.host}`);
const streamUrl = `http://${window.location.hostname}:4912/embed`;

let reloadTimer;
let streamLoaded = false;

// ── Stream ────────────────────────────────────────────────

function loadStream() {
    if (!streamLoaded) {
        cameraStream.src = streamUrl;
    }
}

cameraStream.addEventListener('load', () => {
    streamLoaded = true;
    clearInterval(reloadTimer);
    cameraStream.style.display = 'block';
    videoPlaceholder.style.display = 'none';
    statusIndicator.className = 'status-indicator on';
    statusText.textContent = 'Show your hand to the camera';
});

// ── Socket ────────────────────────────────────────────────

function setDefaultUI() {
    statusIndicator.className = 'status-indicator';
    statusText.textContent = 'Connecting...';
    currentGesture.textContent = 'Waiting...';
    gestureConfidence.textContent = 'Confidence: --';
    lastAction.textContent = '';
}

document.addEventListener('DOMContentLoaded', () => {
    setDefaultUI();
    loadStream();
    reloadTimer = setInterval(loadStream, 1000);
});

socket.on('connect', () => {
    statusIndicator.className = 'status-indicator on';
    statusText.textContent = 'Connected';
});

socket.on('disconnect', () => {
    statusIndicator.className = 'status-indicator error';
    statusText.textContent = 'Disconnected';
});

socket.on('gesture_result', (message) => {
    if (!message) return;

    currentGesture.textContent = message.gesture || 'Waiting...';
    gestureConfidence.textContent = message.confidence
        ? `Confidence: ${message.confidence}%`
        : 'Confidence: --';
    lastAction.textContent = message.action || '';
});
