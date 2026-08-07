// SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
//
// SPDX-License-Identifier: MPL-2.0

const ledButton = document.getElementById('led-button');
const statusDot = document.getElementById('status-dot');
const statusLabel = document.getElementById('status-label');
const statusText = document.getElementById('status-text');
const errorContainer = document.getElementById('error-container');

const socket = io(`http://${window.location.host}`);

// Set default UI state immediately — matches HTML, no socket needed
function setDefaultUI() {
    ledButton.className = 'led-off';
    ledButton.textContent = 'LED IS OFF';
    statusDot.className = 'status-indicator';
    statusLabel.textContent = 'Ready';
    statusText.textContent = 'Click to control the LED';
    errorContainer.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    setDefaultUI();
    initSocketIO();
    ledButton.addEventListener('click', handleLedClick);
});

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

    socket.on('led_status_update', (message) => {
        const isOn = message.led_is_on;
        ledButton.className = isOn ? 'led-on' : 'led-off';
        ledButton.textContent = isOn ? 'LED IS ON' : 'LED IS OFF';
        statusText.textContent = 'Click to control the LED';
    });

    socket.on('disconnect', () => {
        setStatus('error');
        errorContainer.textContent = 'Connection lost. Check your board and try again.';
        errorContainer.style.display = 'block';
    });
}

function handleLedClick() {
    socket.emit('toggle_led', {});
}
