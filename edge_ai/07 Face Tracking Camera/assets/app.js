// SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
//
// SPDX-License-Identifier: MPL-2.0

const socket = io(`http://${window.location.host}`);

const statusDot = document.getElementById("status-dot");
const statusLabel = document.getElementById("status-label");
const statusText = document.getElementById("status-text");
const faceStatus = document.getElementById("face-status");
const errorContainer = document.getElementById("error-container");

const iframe = document.getElementById("camera-stream");

const streamUrl =
    `http://${window.location.hostname}:4912/embed`;

let streamRetryTimer = null;

function loadCameraStream() {
    iframe.src = streamUrl;
}

iframe.addEventListener("load", () => {
    if (streamRetryTimer) {
        clearInterval(streamRetryTimer);
        streamRetryTimer = null;
    }

    iframe.style.display = "block";
});

document.addEventListener("DOMContentLoaded", () => {
    loadCameraStream();
    streamRetryTimer = setInterval(loadCameraStream, 1000);
});

socket.on("connect", () => {
    statusDot.className = "status-indicator on";
    statusLabel.textContent = "Connected";
    errorContainer.style.display = "none";
});

socket.on("disconnect", () => {
    statusDot.className = "status-indicator error";
    statusLabel.textContent = "Disconnected";
    errorContainer.textContent =
        "Connection lost. Check the board and run the app again.";
    errorContainer.style.display = "block";
});

socket.on("face_status", (message) => {
    const detected = Boolean(message.detected);

    faceStatus.textContent = detected
        ? "Face detected"
        : "Looking for a face";

    faceStatus.classList.toggle("detected", detected);

    statusText.textContent = detected
        ? "The pan and tilt servos are following the face."
        : "The pan-tilt is centered and waiting.";
});
