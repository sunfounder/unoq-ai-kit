// SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
//
// SPDX-License-Identifier: MPL-2.0

const socket = io(`http://${window.location.host}`);

const statusDot = document.getElementById('status-dot');
const statusLabel = document.getElementById('status-label');
const chatBox = document.getElementById('chat-box');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const petPreview = document.getElementById('pet-preview');
const emotionName = document.getElementById('emotion-name');
const errorContainer = document.getElementById('error-container');
const characterCount = document.getElementById('character-count');

const petFaces = {
    neutral: '• — •',
    happy: '• ◡ •',
    sad: '• ︵ •',
    surprised: '• ○ •',
    thinking: '• ? •',
};

let waitingForReply = false;

function updateCharacterCount() {
    characterCount.textContent = `${messageInput.value.length} / 300`;
}

function addMessage(role, text) {
    const div = document.createElement('div');
    div.className = `msg ${role}`;
    div.textContent = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function setEmotion(emotion) {
    const safeEmotion = petFaces[emotion] ? emotion : 'neutral';
    petPreview.textContent = petFaces[safeEmotion];
    petPreview.className = `pet-preview ${safeEmotion}`;
    emotionName.textContent = safeEmotion;
}

function setWaiting(waiting) {
    waitingForReply = waiting;
    sendBtn.disabled = waiting;
    messageInput.disabled = waiting;
    sendBtn.textContent = waiting ? 'Thinking…' : 'Send';
}

function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || waitingForReply) return;

    addMessage('user', text);
    socket.emit('message', { text });
    messageInput.value = '';
    setEmotion('thinking');
    setWaiting(true);
}

sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});
messageInput.addEventListener('input', updateCharacterCount);

socket.on('connect', () => {
    statusDot.className = 'status-indicator on';
    statusLabel.textContent = 'Connected';
    errorContainer.style.display = 'none';
});

socket.on('pet_status', (data) => {
    setEmotion(data.emotion || 'thinking');
});

socket.on('response', (data) => {
    setEmotion(data.emotion || 'neutral');
    addMessage('bot', data.reply || 'I am here with you.');
    setWaiting(false);
    messageInput.focus();
});

socket.on('disconnect', () => {
    statusDot.className = 'status-indicator error';
    statusLabel.textContent = 'Disconnected';
    setWaiting(false);
});

document.addEventListener('DOMContentLoaded', () => {
    setEmotion('neutral');
    updateCharacterCount();
});
