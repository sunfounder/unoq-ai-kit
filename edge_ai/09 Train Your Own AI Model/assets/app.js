// SPDX-FileCopyrightText: Copyright (C) SunFounder
//
// SPDX-License-Identifier: MPL-2.0

const socket = io(`http://${window.location.host}`);

const statusDot = document.getElementById('status-dot');
const statusLabel = document.getElementById('status-label');
const errorContainer = document.getElementById('error-container');
const iframe = document.getElementById('camera-stream');
const placeholder = document.querySelector('.camera-placeholder');
const detectionsBox = document.getElementById('detections');
const totalsBox = document.getElementById('totals');
const sessionTime = document.getElementById('session-time');
const sessionDetections = document.getElementById('session-detections');
const sessionClasses = document.getElementById('session-classes');

const streamUrl = `http://${window.location.hostname}:4912/embed`;
let streamLoaded = false;

function setStatus(state, label) {
    statusDot.className = `status-indicator ${state}`;
    statusLabel.textContent = label;
}

// Class names come from your own dataset, so they are escaped before they
// are put on the page.
function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, character => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[character]));
}

// ── Live camera preview ───────────────────────────────────────────
// The AI brick serves the video it analyses on port 4912.

function loadStream() {
    if (!streamLoaded) {
        iframe.src = streamUrl;
    }
}

iframe.addEventListener('load', () => {
    streamLoaded = true;
    iframe.style.display = 'block';
    if (placeholder) {
        placeholder.style.display = 'none';
    }
    setStatus('on', 'Connected');
});

// ── Results ───────────────────────────────────────────────────────

function renderDetections(objects) {
    if (!objects || objects.length === 0) {
        detectionsBox.innerHTML = '<p class="empty">Nothing yet - point the camera at your object.</p>';
        return;
    }

    detectionsBox.innerHTML = objects.map(item => `
        <div class="detection">
            <div class="detection-head">
                <span class="detection-name">${escapeHtml(item.object)}</span>
                <span class="detection-confidence">${item.confidence}%</span>
            </div>
            <div class="confidence-bar">
                <div style="width: ${Math.max(2, Math.min(100, item.confidence))}%"></div>
            </div>
        </div>`).join('');
}

function renderTotals(totals) {
    if (!totals || totals.length === 0) {
        totalsBox.innerHTML = '<p class="empty">No classes seen yet.</p>';
        return;
    }

    totalsBox.innerHTML = totals.map(item => `
        <div class="total">
            <span class="total-name">${escapeHtml(item.object)}</span>
            <span class="total-count">${item.count}</span>
        </div>`).join('');
}

socket.on('model_report', data => {
    renderDetections(data.objects);
    renderTotals(data.totals);
    sessionTime.textContent = `${data.minutes}:${String(data.seconds).padStart(2, '0')}`;
    sessionDetections.textContent = data.detections;
    sessionClasses.textContent = data.classes;
});

socket.on('connect', () => {
    setStatus('on', 'Connected');
    loadStream();
});

socket.on('disconnect', () => {
    setStatus('off', 'Disconnected');
    errorContainer.textContent = 'Connection to the app was lost.';
    errorContainer.style.display = 'block';
});

loadStream();
