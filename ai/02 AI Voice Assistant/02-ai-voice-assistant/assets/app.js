// SPDX-FileCopyrightText: Copyright (C) SunFounder
//
// SPDX-License-Identifier: MPL-2.0

const socket = io(`http://${window.location.host}`);

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

let holding = false;
let busy = false;

const stateTitles = {
    ready: 'Ready',
    listening: 'Listening',
    recognizing: 'Recognizing',
    thinking: 'Thinking',
    speaking: 'Speaking',
    error: 'Error',
};

function updateState(data) {
    const state = data.state || 'ready';

    statusPanel.className = `status-panel ${state}`;
    statusTitle.textContent = stateTitles[state] || state;
    statusMessage.textContent = data.message || '';

    busy = ['recognizing', 'thinking', 'speaking'].includes(state);
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

talkButton.addEventListener('pointerdown', beginRecording);
talkButton.addEventListener('pointerup', finishRecording);
talkButton.addEventListener('pointercancel', finishRecording);

window.addEventListener('blur', () => {
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
});

socket.on('connect', () => {
    statusDot.className = 'status-indicator on';
    statusLabel.textContent = 'Connected';

    updateState({
        state: 'ready',
        message: 'Hold the button and speak.',
    });
});

socket.on('voice_status', updateState);

socket.on('disconnect', () => {
    holding = false;
    busy = false;
    talkButton.classList.remove('active');
    talkButton.disabled = true;

    statusDot.className = 'status-indicator error';
    statusLabel.textContent = 'Disconnected';

    updateState({
        state: 'error',
        message: 'Connection to the app was lost.',
    });
});
