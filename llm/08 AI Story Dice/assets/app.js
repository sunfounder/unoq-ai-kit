// SPDX-FileCopyrightText: Copyright (C) SunFounder
// SPDX-License-Identifier: MPL-2.0

const socket = io(`http://${window.location.host}`);
const statusDot = document.getElementById('status-dot');
const connectionLabel = document.getElementById('connection-label');
const cameraStream = document.getElementById('camera-stream');
const genreSelect = document.getElementById('genre-select');
const createButton = document.getElementById('create-button');
const statusPanel = document.getElementById('status-panel');
const statusTitle = document.getElementById('status-title');
const statusMessage = document.getElementById('status-message');
const objectList = document.getElementById('object-list');
const storyCard = document.getElementById('story-card');
const storyTitle = document.getElementById('story-title');
const storyText = document.getElementById('story-text');
const errorContainer = document.getElementById('error-container');

let busy = false;
let streamRetryTimer = null;
const stateTitles = {
    ready: 'Ready',
    capturing: 'Image Captured',
    thinking: 'AI Is Writing',
    speaking: 'Reading Your Story',
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

function showObjects(objects) {
    objectList.replaceChildren();
    if (!objects || objects.length === 0) {
        const empty = document.createElement('span');
        empty.className = 'empty-text';
        empty.textContent = 'Your objects will appear here.';
        objectList.appendChild(empty);
        return;
    }
    objects.forEach((name) => {
        const chip = document.createElement('span');
        chip.className = 'object-chip';
        chip.textContent = name;
        objectList.appendChild(chip);
    });
}

function updateState(data) {
    const state = data.state || 'ready';
    busy = ['capturing', 'thinking', 'speaking'].includes(state);
    statusPanel.className = `status-panel ${state}`;
    statusTitle.textContent = stateTitles[state] || state;
    statusMessage.textContent = data.message || '';
    createButton.disabled = busy || !socket.connected;
    genreSelect.disabled = busy;

    if (data.result) {
        showObjects(data.result.objects);
        storyTitle.textContent = data.result.title || 'AI Story';
        storyText.textContent = data.result.story || '';
        storyCard.className = `story-card ${data.result.mood || 'calm'}`;
    }

    if (state === 'error') {
        errorContainer.textContent = data.message || 'Unknown error';
        errorContainer.style.display = 'block';
    } else {
        errorContainer.textContent = '';
        errorContainer.style.display = 'none';
    }
}

createButton.addEventListener('click', () => {
    if (busy || !socket.connected) return;
    updateState({
        state: 'capturing',
        message: 'Capturing the objects in front of the camera...',
    });
    socket.emit('create_story', { genre: genreSelect.value });
});

socket.on('connect', () => {
    statusDot.className = 'status-indicator on';
    connectionLabel.textContent = 'Connected';
    loadCameraStream();
    socket.emit('get_state', {});
});

socket.on('story_state', updateState);

socket.on('disconnect', () => {
    clearTimeout(streamRetryTimer);
    cameraStream.removeAttribute('src');
    statusDot.className = 'status-indicator error';
    connectionLabel.textContent = 'Disconnected';
    updateState({ state: 'error', message: 'Connection to the app was lost.' });
});

