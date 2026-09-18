// SPDX-FileCopyrightText: Copyright (C) SunFounder
//
// SPDX-License-Identifier: MPL-2.0

const socket = io(`http://${window.location.host}`);

const statusDot = document.getElementById('status-dot');
const connectionLabel = document.getElementById('connection-label');
const statusPanel = document.getElementById('status-panel');
const statusTitle = document.getElementById('status-title');
const statusMessage = document.getElementById('status-message');
const questionForm = document.getElementById('question-form');
const questionInput = document.getElementById('question-input');
const askButton = document.getElementById('ask-button');
const answerText = document.getElementById('answer-text');
const errorContainer = document.getElementById('error-container');
const cameraStream = document.getElementById('camera-stream');

let busy = false;
let streamRetryTimer = null;

const stateTitles = {
    ready: 'Ready',
    capturing: 'Image Captured',
    thinking: 'Thinking',
    speaking: 'Speaking',
    error: 'Error',
};

function updateState(data) {
    const state = data.state || 'ready';

    statusPanel.className = `status-panel ${state}`;
    statusTitle.textContent = stateTitles[state] || state;
    statusMessage.textContent = data.message || '';

    busy = ['capturing', 'thinking', 'speaking'].includes(state);
    askButton.disabled = busy || !socket.connected;
    questionInput.disabled = busy;
    askButton.textContent = busy ? 'PLEASE WAIT' : 'ASK AI';

    if (data.answer) {
        answerText.textContent = data.answer;
    }

    if (state === 'error') {
        errorContainer.textContent = data.message || 'Unknown error';
        errorContainer.style.display = 'block';
    } else {
        errorContainer.textContent = '';
        errorContainer.style.display = 'none';
    }
}

function loadCameraStream() {
    clearTimeout(streamRetryTimer);
    cameraStream.src = `http://${window.location.hostname}:7000/stream?r=${Date.now()}`;
}

cameraStream.addEventListener('error', () => {
    clearTimeout(streamRetryTimer);
    streamRetryTimer = setTimeout(loadCameraStream, 1500);
});

questionForm.addEventListener('submit', (event) => {
    event.preventDefault();

    const question = questionInput.value.trim();
    if (!question || busy || !socket.connected) {
        return;
    }

    updateState({
        state: 'capturing',
        message: 'Capturing the current camera image...',
    });

    socket.emit('ask_ai', { question });
});

socket.on('connect', () => {
    statusDot.className = 'status-indicator on';
    connectionLabel.textContent = 'Connected';

    updateState({
        state: 'ready',
        message: 'Ask a question about the camera image.',
    });

    loadCameraStream();
});

socket.on('vision_status', updateState);

socket.on('disconnect', () => {
    clearTimeout(streamRetryTimer);
    cameraStream.removeAttribute('src');
    busy = false;
    askButton.disabled = true;
    questionInput.disabled = false;

    statusDot.className = 'status-indicator error';
    connectionLabel.textContent = 'Disconnected';

    updateState({
        state: 'error',
        message: 'Connection to the app was lost.',
    });
});
