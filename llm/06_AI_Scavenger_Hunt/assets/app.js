// SPDX-FileCopyrightText: Copyright (C) SunFounder
// SPDX-License-Identifier: MPL-2.0

const socket = io(`http://${window.location.host}`);

const statusDot = document.getElementById('status-dot');
const connectionLabel = document.getElementById('connection-label');
const statusPanel = document.getElementById('status-panel');
const statusTitle = document.getElementById('status-title');
const statusMessage = document.getElementById('status-message');
const missionText = document.getElementById('mission-text');
const scoreValue = document.getElementById('score-value');
const attemptsValue = document.getElementById('attempts-value');
const resultCard = document.getElementById('result-card');
const resultText = document.getElementById('result-text');
const cameraStream = document.getElementById('camera-stream');
const newButton = document.getElementById('new-button');
const checkButton = document.getElementById('check-button');
const resetButton = document.getElementById('reset-button');
const errorContainer = document.getElementById('error-container');

let busy = false;
let hasMission = false;
let streamRetryTimer = null;

const stateTitles = {
    ready: 'Ready',
    generating: 'Creating Mission',
    capturing: 'Image Captured',
    thinking: 'AI Referee Is Thinking',
    speaking: 'Speaking',
    success: 'Success!',
    try_again: 'Try Again',
    complete: 'Mission Complete',
    error: 'Error',
};

function loadCameraStream() {
    clearTimeout(streamRetryTimer);
    cameraStream.src = `http://${window.location.hostname}:7000/stream?r=${Date.now()}`;
}

cameraStream.addEventListener('error', () => {
    clearTimeout(streamRetryTimer);
    streamRetryTimer = setTimeout(loadCameraStream, 1500);
});

function updateButtons(state) {
    busy = ['generating', 'capturing', 'thinking', 'speaking', 'success', 'try_again'].includes(state);
    const connected = socket.connected;
    newButton.disabled = busy || !connected;
    checkButton.disabled = busy || !connected || !hasMission || state === 'complete';
    resetButton.disabled = busy || !connected;
}

function updateState(data) {
    const state = data.state || 'ready';
    const previousMission = hasMission ? missionText.textContent : '';
    const incomingMission = data.task || '';
    const missionChanged = Boolean(incomingMission && incomingMission !== previousMission);

    hasMission = Boolean(incomingMission);
    missionText.textContent = incomingMission || 'Choose NEW MISSION to begin.';
    scoreValue.textContent = Number(data.score || 0);
    attemptsValue.textContent = Number(data.attempts || 0);

    statusPanel.className = `status-panel ${state}`;
    statusTitle.textContent = stateTitles[state] || state;
    statusMessage.textContent = data.message || '';

    resultCard.className = `result-card ${state}`;
    if (data.result) {
        resultText.textContent = data.result;
    } else if (state === 'generating') {
        resultText.textContent = 'Waiting for a new mission...';
    } else if (missionChanged) {
        resultText.textContent = 'Show an object and let the AI referee check it.';
    } else if (!hasMission) {
        resultText.textContent = 'The AI result will appear here.';
    }

    if (state === 'error') {
        errorContainer.textContent = data.message || 'Unknown error';
        errorContainer.style.display = 'block';
    } else {
        errorContainer.textContent = '';
        errorContainer.style.display = 'none';
    }

    updateButtons(state);
}

newButton.addEventListener('click', () => {
    if (busy || !socket.connected) return;
    updateState({
        state: 'generating',
        message: 'AI is creating a new mission...',
        task: missionText.textContent.startsWith('Choose') ? '' : missionText.textContent,
        score: scoreValue.textContent,
        attempts: attemptsValue.textContent,
    });
    socket.emit('new_mission', {});
});

checkButton.addEventListener('click', () => {
    if (busy || !hasMission || !socket.connected) return;
    updateState({
        state: 'capturing',
        message: 'Capturing the current camera image...',
        task: missionText.textContent,
        score: scoreValue.textContent,
        attempts: attemptsValue.textContent,
    });
    socket.emit('check_object', {});
});

resetButton.addEventListener('click', () => {
    if (busy || !socket.connected) return;
    socket.emit('reset_game', {});
});

socket.on('connect', () => {
    statusDot.className = 'status-indicator on';
    connectionLabel.textContent = 'Connected';
    loadCameraStream();
    socket.emit('get_state', {});
});

socket.on('game_state', updateState);

socket.on('disconnect', () => {
    clearTimeout(streamRetryTimer);
    cameraStream.removeAttribute('src');
    statusDot.className = 'status-indicator error';
    connectionLabel.textContent = 'Disconnected';
    updateState({
        state: 'error',
        message: 'Connection to the app was lost.',
        task: hasMission ? missionText.textContent : '',
        score: scoreValue.textContent,
        attempts: attemptsValue.textContent,
    });
});
