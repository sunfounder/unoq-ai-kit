const connectionDot = document.getElementById('connection-dot');
const connectionLabel = document.getElementById('connection-label');
const errorContainer = document.getElementById('error-container');
const cameraStream = document.getElementById('camera-stream');
const detectionStatus = document.getElementById('detection-status');
const detectionText = document.getElementById('detection-text');
const confidenceText = document.getElementById('confidence-text');
const totalCount = document.getElementById('total-count');
const resetButton = document.getElementById('reset-counts');

const countElements = {
    mouse: document.getElementById('mouse-count'),
    keyboard: document.getElementById('keyboard-count'),
    'cell phone': document.getElementById('phone-count'),
};

const displayNames = {
    mouse: 'Mouse',
    keyboard: 'Keyboard',
    'cell phone': 'Cell Phone',
};

const socket = io(`http://${window.location.host}`);
const streamUrl = `http://${window.location.hostname}:4912/embed`;

let previousCounts = {
    mouse: 0,
    keyboard: 0,
    'cell phone': 0,
};

function setConnectionStatus(state, label) {
    connectionDot.className = `status-indicator ${state}`;
    connectionLabel.textContent = label;
}

function showError(message) {
    errorContainer.textContent = message;
    errorContainer.style.display = 'block';
}

function clearError() {
    errorContainer.textContent = '';
    errorContainer.style.display = 'none';
}

function animateCard(label) {
    const card = document.querySelector(
        `.counter-card[data-object="${label}"]`
    );

    if (!card) return;

    card.classList.remove('counted');
    void card.offsetWidth;
    card.classList.add('counted');

    window.setTimeout(() => {
        card.classList.remove('counted');
    }, 700);
}

function renderState(state, animate = true) {
    if (!state || !state.counts) return;

    Object.entries(countElements).forEach(([label, element]) => {
        const value = Number(state.counts[label] || 0);

        if (animate && value > previousCounts[label]) {
            animateCard(label);
        }

        element.textContent = value;
        previousCounts[label] = value;
    });

    totalCount.textContent = Number(state.total || 0);

    if (state.last_detection) {
        const label = state.last_detection.object;
        detectionStatus.classList.add('detected');
        detectionText.textContent =
            `${displayNames[label] || label} added`;
        confidenceText.textContent =
            `Confidence: ${state.last_detection.confidence}%`;
    } else {
        detectionStatus.classList.remove('detected');
        detectionText.textContent = 'Show one object to the camera';
        confidenceText.textContent = 'Mouse, keyboard, or cell phone';
    }
}

async function loadState() {
    try {
        const response = await fetch('/state');
        if (!response.ok) throw new Error('Request failed');
        renderState(await response.json(), false);
    } catch (error) {
        showError('Could not load the counter state. Please try again.');
    }
}

cameraStream.src = streamUrl;

socket.on('connect', () => {
    setConnectionStatus('on', 'Connected');
    clearError();
    loadState();
});

socket.on('counter_state', state => {
    renderState(state, true);
});

socket.on('disconnect', () => {
    setConnectionStatus('error', 'Disconnected');
    showError('Connection lost. Check the board and run the App again.');
});

resetButton.addEventListener('click', async () => {
    resetButton.disabled = true;

    try {
        const response = await fetch('/reset-counts', {
            method: 'POST',
        });
        if (!response.ok) throw new Error('Request failed');
        renderState(await response.json(), false);
        clearError();
    } catch (error) {
        showError('Could not reset the counts. Please try again.');
    } finally {
        resetButton.disabled = false;
    }
});
