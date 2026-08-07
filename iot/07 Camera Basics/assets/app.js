// SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
//
// SPDX-License-Identifier: MPL-2.0

const statusDot = document.getElementById('status-dot');
const statusLabel = document.getElementById('status-label');
const statusText = document.getElementById('status-text');
const errorContainer = document.getElementById('error-container');
const iframe = document.getElementById('camera-stream');
const placeholder = document.getElementById('video-placeholder');

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

document.addEventListener('DOMContentLoaded', () => {
    setStatus('', 'Connecting');
    loadStream();
    reloadTimer = setInterval(loadStream, 1000);
});

iframe.addEventListener('load', () => {
    streamLoaded = true;
    clearInterval(reloadTimer);
    placeholder.style.display = 'none';
    iframe.style.display = 'block';
    setStatus('on', 'Connected');
    statusText.textContent = 'Live camera preview';
});

socket.on('connect', () => {
    errorContainer.style.display = 'none';
    errorContainer.textContent = '';
});

socket.on('disconnect', () => {
    setStatus('error', 'Disconnected');
    statusText.textContent = 'Camera preview unavailable';
    errorContainer.textContent = 'Connection lost. Check the board and run the app again.';
    errorContainer.style.display = 'block';
});
