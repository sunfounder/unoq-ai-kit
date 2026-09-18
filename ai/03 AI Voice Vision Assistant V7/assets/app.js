// SPDX-FileCopyrightText: Copyright (C) SunFounder
//
// SPDX-License-Identifier: MPL-2.0

const socket = io(`http://${window.location.host}`);
const streamUrl = `http://${window.location.hostname}:4912/embed`;

const statusDot = document.getElementById('status-dot');
const statusLabel = document.getElementById('status-label');
const statusPanel = document.getElementById('status-panel');
const statusTitle = document.getElementById('status-title');
const statusMessage = document.getElementById('status-message');

const talkButton = document.getElementById('talk-button');
const buttonLabel = document.getElementById('button-label');
const heardText = document.getElementById('heard-text');
const replyText = document.getElementById('reply-text');
const errorContainer = document.getElementById('error-container');
const ledIndicator = document.getElementById('led-indicator');

const cameraToggle = document.getElementById('camera-toggle');
const cameraStatusText = document.getElementById('camera-status-text');
const iframe = document.getElementById('camera-stream');
const placeholder = document.getElementById('video-placeholder');
const placeholderText = document.getElementById('placeholder-text');

let holding = false;
let busy = false;
let cameraOn = true;
let streamLoaded = false;
let reloadTimer = null;

const stateTitles = {
    ready: 'Ready',
    listening: 'Listening',
    recognizing: 'Recognizing',
    looking: 'Looking',
    thinking: 'Thinking',
    speaking: 'Speaking',
    error: 'Error',
};

function updateLed(isOn) {
    ledIndicator.className = isOn
        ? 'led-indicator active'
        : 'led-indicator';
}

function loadStream() {
    if (!cameraOn || streamLoaded) {
        return;
    }

    iframe.src = streamUrl;
}

function startStreamLoading() {
    if (!cameraOn) {
        return;
    }

    placeholder.style.display = 'flex';
    iframe.style.display = 'none';
    placeholderText.textContent = 'Searching for camera...';
    cameraStatusText.textContent = 'Connecting to live camera...';

    loadStream();

    if (reloadTimer === null) {
        reloadTimer = window.setInterval(loadStream, 1000);
    }
}

function stopStreamLoading() {
    if (reloadTimer !== null) {
        window.clearInterval(reloadTimer);
        reloadTimer = null;
    }
}

function turnCameraOn() {
    cameraOn = true;
    streamLoaded = false;
    cameraToggle.textContent = 'Camera ON';
    cameraToggle.className = 'camera-toggle on';
    startStreamLoading();
}

function turnCameraOff() {
    cameraOn = false;
    streamLoaded = false;
    stopStreamLoading();

    iframe.style.display = 'none';
    iframe.src = 'about:blank';
    placeholder.style.display = 'flex';
    placeholderText.textContent = 'Camera display is off';
    cameraStatusText.textContent = 'Camera display off';

    cameraToggle.textContent = 'Camera OFF';
    cameraToggle.className = 'camera-toggle off';
}

function updateState(data) {
    const state = data.state || 'ready';

    statusPanel.className = `status-panel ${state}`;
    statusTitle.textContent = stateTitles[state] || state;
    statusMessage.textContent = data.message || '';

    busy = ['recognizing', 'looking', 'thinking', 'speaking'].includes(state);
    talkButton.disabled = busy || !socket.connected;

    if (state === 'listening') {
        buttonLabel.textContent = 'Release to Finish';
    } else if (busy) {
        buttonLabel.textContent = 'Please Wait';
    } else {
        buttonLabel.textContent = 'Hold to Speak';
    }

    if (data.heard) {
        heardText.textContent = data.heard;
    }

    if (data.reply) {
        replyText.textContent = data.reply;
    }

    if (typeof data.led_on === 'boolean') {
        updateLed(data.led_on);
    }

    if (state === 'error') {
        errorContainer.textContent = data.message || 'Unknown error';
        errorContainer.style.display = 'block';
    } else {
        errorContainer.textContent = '';
        errorContainer.style.display = 'none';
    }
}

function beginRecording(event) {
    event.preventDefault();

    if (holding || busy || !socket.connected) {
        return;
    }

    holding = true;
    talkButton.classList.add('active');

    if (talkButton.setPointerCapture) {
        talkButton.setPointerCapture(event.pointerId);
    }

    updateState({
        state: 'listening',
        message: 'Listening... Release the button when you finish speaking.',
    });

    socket.emit('start_recording', {});
}

function finishRecording(event) {
    event.preventDefault();

    if (!holding) {
        return;
    }

    holding = false;
    talkButton.classList.remove('active');

    updateState({
        state: 'recognizing',
        message: 'Recognizing your speech...',
    });

    socket.emit('stop_recording', {});
}

cameraToggle.addEventListener('click', () => {
    if (cameraOn) {
        turnCameraOff();
    } else {
        turnCameraOn();
    }
});

talkButton.addEventListener('pointerdown', beginRecording);
talkButton.addEventListener('pointerup', finishRecording);
talkButton.addEventListener('pointercancel', finishRecording);

iframe.addEventListener('load', () => {
    if (!cameraOn || iframe.src === 'about:blank') {
        return;
    }

    streamLoaded = true;
    stopStreamLoading();
    placeholder.style.display = 'none';
    iframe.style.display = 'block';
    cameraStatusText.textContent = 'Live camera preview';
});

socket.on('connect', () => {
    statusDot.className = 'status-indicator on';
    statusLabel.textContent = 'Connected';
    talkButton.disabled = false;
    errorContainer.style.display = 'none';

    updateState({
        state: 'ready',
        message: 'Hold the button and speak.',
    });
});

socket.on('voice_status', updateState);

socket.on('led_status', (data) => {
    updateLed(Boolean(data.on));
});

socket.on('disconnect', () => {
    holding = false;
    busy = false;
    talkButton.classList.remove('active');
    talkButton.disabled = true;

    statusDot.className = 'status-indicator error';
    statusLabel.textContent = 'Disconnected';
    statusPanel.className = 'status-panel error';
    statusTitle.textContent = 'Disconnected';
    statusMessage.textContent = 'Connection to the app was lost.';
});

document.addEventListener('DOMContentLoaded', turnCameraOn);
