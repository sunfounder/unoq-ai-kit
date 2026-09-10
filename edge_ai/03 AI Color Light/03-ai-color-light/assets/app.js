// SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
//
// SPDX-License-Identifier: MPL-2.0

const statusDot = document.getElementById('status-dot');
const statusLabel = document.getElementById('status-label');
const statusText = document.getElementById('status-text');
const errorContainer = document.getElementById('error-container');
const iframe = document.getElementById('camera-stream');
const objectName = document.getElementById('object-name');
const colorName = document.getElementById('color-name');
const confidenceValue = document.getElementById('confidence-value');
const colorPreview = document.getElementById('color-preview');

const socket = io(`http://${window.location.host}`);
const streamUrl = `http://${window.location.hostname}:4912/embed`;

let reloadTimer;
let streamLoaded = false;

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
    iframe.style.display = 'block';
    setStatus('on', 'Connected');
    statusText.textContent = 'Edge AI is detecting objects locally';
});

document.addEventListener('DOMContentLoaded', () => {
    setStatus('', 'Connecting');
    loadStream();
    reloadTimer = setInterval(loadStream, 1000);
});

socket.on('connect', () => {
    errorContainer.style.display = 'none';
    errorContainer.textContent = '';
});

socket.on('object_color', (data) => {
    if (!data) return;

    objectName.textContent = data.object || 'Unknown';
    colorName.textContent = data.color || 'Off';
    confidenceValue.textContent = data.confidence
        ? `${data.confidence}%`
        : '--';

    colorPreview.style.background = data.hex || '#dfe6e9';
    colorPreview.classList.toggle('off', data.color === 'Off');
});

socket.on('disconnect', () => {
    setStatus('error', 'Disconnected');
    statusText.textContent = 'Detection unavailable';
    errorContainer.textContent = 'Connection lost. Check the board and try again.';
    errorContainer.style.display = 'block';
});
