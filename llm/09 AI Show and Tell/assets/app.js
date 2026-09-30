// SPDX-FileCopyrightText: Copyright (C) SunFounder
// SPDX-License-Identifier: MPL-2.0

const socket = io(`http://${window.location.host}`);

const statusDot = document.getElementById('status-dot');
const connectionLabel = document.getElementById('connection-label');
const cameraStream = document.getElementById('camera-stream');
const statusPanel = document.getElementById('status-panel');
const statusTitle = document.getElementById('status-title');
const statusMessage = document.getElementById('status-message');
const speakButton = document.getElementById('speak-button');
const buttonLabel = document.getElementById('button-label');
const heardText = document.getElementById('heard-text');
const answerText = document.getElementById('answer-text');
const errorContainer = document.getElementById('error-container');

let recording = false;
let busy = false;
let streamRetryTimer = null;
let recordingTimer = null;

const stateTitles = {
    ready: 'Ready',
    listening: 'Listening',
    capturing: 'Captured',
    recognizing: 'Recognizing Speech',
    thinking: 'AI Is Looking',
    speaking: 'Speaking',
    error: 'Something Went Wrong',
};

function loadCameraStream() {
    clearTimeout(streamRetryTimer);
    cameraStream.src = `http://${window.location.hostname}:7000/stream?r=${Date.now()}`;
}

cameraStream.addEventListener('error', () => {
    clearTimeout(streamRetryTimer);
    streamRetryTimer = setTimeout(loadCameraStream, 1500);
});

function updateButton() {
    speakButton.disabled = !socket.connected || busy;
    speakButton.classList.toggle('recording', recording);
    buttonLabel.textContent = recording ? 'Listening... Release to Send' : 'Hold to Speak';
}

function stopRecording() {
    if (!recording) return;
    recording = false;
    clearTimeout(recordingTimer);
    socket.emit('stop_recording', {});
    updateButton();
}

function updateState(data) {
    const state = data.state || 'ready';
    recording = state === 'listening';
    busy = ['capturing', 'recognizing', 'thinking', 'speaking'].includes(state);

    statusPanel.className = `status-panel ${state}`;
    statusTitle.textContent = stateTitles[state] || state;
    statusMessage.textContent = data.message || '';

    if (data.question) heardText.textContent = data.question;
    if (data.answer) answerText.textContent = data.answer;

    if (state === 'error') {
        errorContainer.textContent = data.message || 'Unknown error';
        errorContainer.style.display = 'block';
    } else {
        errorContainer.textContent = '';
        errorContainer.style.display = 'none';
    }
    updateButton();
}

speakButton.addEventListener('pointerdown', (event) => {
    if (busy || recording || !socket.connected) return;
    event.preventDefault();
    speakButton.setPointerCapture(event.pointerId);
    recording = true;
    socket.emit('start_recording', {});
    updateButton();

    // Prevent an accidental endless recording while keeping more time than
    // the earlier fixed five-second recordings.
    recordingTimer = setTimeout(stopRecording, 15000);
});

speakButton.addEventListener('pointerup', (event) => {
    event.preventDefault();
    stopRecording();
});
speakButton.addEventListener('pointercancel', stopRecording);
speakButton.addEventListener('lostpointercapture', stopRecording);
window.addEventListener('blur', stopRecording);

socket.on('connect', () => {
    statusDot.className = 'status-indicator on';
    connectionLabel.textContent = 'Connected';
    loadCameraStream();
    socket.emit('get_state', {});
});

socket.on('show_tell_status', updateState);

socket.on('disconnect', () => {
    clearTimeout(streamRetryTimer);
    clearTimeout(recordingTimer);
    recording = false;
    busy = false;
    cameraStream.removeAttribute('src');
    statusDot.className = 'status-indicator error';
    connectionLabel.textContent = 'Disconnected';
    updateState({
        state: 'error',
        message: 'Connection to the app was lost.',
    });
});

