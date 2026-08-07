// SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
//
// SPDX-License-Identifier: MPL-2.0

const socket = io(`http://${window.location.host}`);

const statusDot = document.getElementById('status-dot');
const statusLabel = document.getElementById('status-label');
const chatBox = document.getElementById('chat-box');
const cmdInput = document.getElementById('command-input');
const sendBtn = document.getElementById('send-btn');
const colorPreview = document.getElementById('color-preview');
const colorName = document.getElementById('color-name');
const errorContainer = document.getElementById('error-container');

// ── Color hex map ─────────────────────────────────────────

const colorHex = {
    'red': '#ef5350', 'green': '#43a047', 'blue': '#1e88e5',
    'yellow': '#fbc02d', 'white': '#fafafa',
};

// ── Send command ──────────────────────────────────────────

function sendCommand() {
    const text = cmdInput.value.trim();
    if (!text) return;

    addMessage('user', text);
    socket.emit('command', { text: text });
    cmdInput.value = '';
}

sendBtn.addEventListener('click', sendCommand);
cmdInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendCommand();
});

// ── Chat ──────────────────────────────────────────────────

function addMessage(role, text) {
    const div = document.createElement('div');
    div.className = `msg ${role}`;
    div.textContent = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function setColor(color) {
    const hex = colorHex[color] || '#cfd8dc';
    colorPreview.style.background = hex;
    colorPreview.classList.toggle('off', !color || color === 'off');
    colorName.textContent = color || 'Off';
}

// ── Socket ────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    statusDot.className = 'status-indicator';
    statusLabel.textContent = 'Ready';
});

socket.on('connect', () => {
    statusDot.className = 'status-indicator on';
    statusLabel.textContent = 'Connected';
    errorContainer.style.display = 'none';
});

socket.on('response', (data) => {
    addMessage('bot', data.text);
    if (data.color) setColor(data.color);
});

socket.on('disconnect', () => {
    statusDot.className = 'status-indicator error';
    statusLabel.textContent = 'Disconnected';
});
