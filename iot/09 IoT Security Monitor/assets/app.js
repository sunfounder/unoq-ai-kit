const connectionDot = document.getElementById('connection-dot');
const connectionLabel = document.getElementById('connection-label');
const errorContainer = document.getElementById('error-container');

const cameraStream = document.getElementById('camera-stream');
const placeholder = document.getElementById('video-placeholder');

const motionCard = document.getElementById('motion-card');
const motionIcon = document.getElementById('motion-icon');
const motionText = document.getElementById('motion-text');

const alarmDot = document.getElementById('alarm-dot');
const alarmText = document.getElementById('alarm-text');

const snapshotText = document.getElementById('snapshot-text');

const eventList = document.getElementById('event-list');
const clearEventsButton = document.getElementById('clear-events');

const socket = io(`http://${window.location.host}`);

let firstFrameReceived = false;

function setConnectionStatus(state, label) {
    connectionDot.className = `status-indicator ${state}`;
    connectionLabel.textContent = label;
}

function showCameraFrame(base64Image) {
    cameraStream.src =
        `data:image/jpeg;base64,${base64Image}`;

    if (!firstFrameReceived) {
        firstFrameReceived = true;
        placeholder.style.display = 'none';
        cameraStream.style.display = 'block';
    }
}

function setMotionStatus(detected) {
    if (detected) {
        motionCard.classList.add('detected');
        motionIcon.textContent = '!';
        motionText.textContent = 'MOTION DETECTED';

        alarmDot.classList.add('on');
        alarmText.classList.add('on');
        alarmText.textContent = 'ON';
    } else {
        motionCard.classList.remove('detected');
        motionIcon.textContent = '✓';
        motionText.textContent = 'AREA CLEAR';

        alarmDot.classList.remove('on');
        alarmText.classList.remove('on');
        alarmText.textContent = 'OFF';
    }
}

function formatTime(date) {
    return date.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
    });
}

function addEvent(message, type) {
    const empty = eventList.querySelector('.empty-events');

    if (empty) {
        empty.remove();
    }

    const row = document.createElement('div');
    row.className = 'event-item';

    const time = document.createElement('span');
    time.className = 'event-time';
    time.textContent = formatTime(new Date());

    const messageBox = document.createElement('div');
    messageBox.className = 'event-message';

    const marker = document.createElement('span');
    marker.className =
        `event-marker ${type === 'motion' ? 'motion' : 'clear'}`;

    const text = document.createElement('span');
    text.textContent = message;

    messageBox.appendChild(marker);
    messageBox.appendChild(text);

    row.appendChild(time);
    row.appendChild(messageBox);

    eventList.prepend(row);

    const rows = eventList.querySelectorAll('.event-item');

    if (rows.length > 10) {
        rows[rows.length - 1].remove();
    }
}

function clearEvents() {
    eventList.innerHTML =
        '<div class="empty-events">No motion events yet.</div>';
}

socket.on('connect', () => {
    setConnectionStatus('on', 'Connected');

    errorContainer.style.display = 'none';
    errorContainer.textContent = '';
});

socket.on('disconnect', () => {
    setConnectionStatus('error', 'Disconnected');

    errorContainer.textContent =
        'Connection lost. Check the board and run the App again.';
    errorContainer.style.display = 'block';
});

socket.on('camera_frame', message => {
    if (!message || !message.image) {
        return;
    }

    showCameraFrame(message.image);
});

socket.on('motion_status', message => {
    if (
        !message ||
        typeof message.detected === 'undefined'
    ) {
        return;
    }

    const detected = Boolean(message.detected);

    setMotionStatus(detected);

    addEvent(
        detected ? 'Motion detected' : 'Area clear',
        detected ? 'motion' : 'clear'
    );
});

socket.on('security_photo', message => {
    if (!message) {
        return;
    }

    const filename = message.filename || 'photo';
    const time = message.time || '';

    snapshotText.textContent =
        `${filename}${time ? ` · ${time}` : ''}`;
});

clearEventsButton.addEventListener('click', clearEvents);
