// SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
//
// SPDX-License-Identifier: MPL-2.0

const socket = io(`http://${window.location.host}`);

const statusDot = document.getElementById('status-dot');
const statusLabel = document.getElementById('status-label');
const guardStatus = document.getElementById('guard-status');
const guardIcon = document.getElementById('guard-icon');
const guardText = document.getElementById('guard-text');
const statusText = document.getElementById('status-text');
const errorContainer = document.getElementById('error-container');
const iframe = document.getElementById('camera-stream');

const streamUrl = `http://${window.location.hostname}:4912/embed`;
let streamLoaded = false;

function loadStream() {
    if (!streamLoaded) iframe.src = streamUrl;
}

iframe.addEventListener('load', () => {
    streamLoaded = true;
    iframe.style.display = 'block';
    statusDot.className = 'status-indicator on';
    statusLabel.textContent = 'Connected';
});

document.addEventListener('DOMContentLoaded', () => {
    loadStream();
    setInterval(loadStream, 1000);
});

socket.on('connect', () => {
    errorContainer.style.display = 'none';
});

socket.on('guard_status', (data) => {
    if (data.alert) {
        guardStatus.className = 'status-alert';
        guardIcon.textContent = '🚨';
        guardText.textContent = `${data.message} (${data.confidence}%)`;
        statusText.textContent = 'ALERT: Intruder detected!';
    } else {
        guardStatus.className = 'status-clear';
        guardIcon.textContent = '🟢';
        guardText.textContent = data.message;
        statusText.textContent = 'AI Smart Guard protecting the perimeter';
    }
});

socket.on('disconnect', () => {
    statusDot.className = 'status-indicator error';
    statusLabel.textContent = 'Disconnected';
    guardStatus.className = 'status-alert';
    guardIcon.textContent = '⚠️';
    guardText.textContent = 'Connection lost';
});
