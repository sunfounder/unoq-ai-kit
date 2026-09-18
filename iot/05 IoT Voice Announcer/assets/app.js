const messageInput = document.getElementById('message-input');
const speakButton = document.getElementById('speak-button');
const statusDot = document.getElementById('status-dot');
const statusLabel = document.getElementById('status-label');
const statusText = document.getElementById('status-text');
const errorContainer = document.getElementById('error-container');
const characterCount = document.getElementById('character-count');

const socket = io(`http://${window.location.host}`);

function updateCharacterCount() {
    characterCount.textContent = `${messageInput.value.length} / 300`;
}

function setConnectionStatus(state) {
    statusDot.className = 'status-indicator ' + state;

    if (state === 'on') {
        statusLabel.textContent = 'Connected';
    } else if (state === 'speaking') {
        statusLabel.textContent = 'Speaking';
    } else if (state === 'error') {
        statusLabel.textContent = 'Disconnected';
    } else {
        statusLabel.textContent = 'Ready';
    }
}

function setSpeaking(isSpeaking) {
    speakButton.disabled = isSpeaking;
    messageInput.disabled = isSpeaking;
    speakButton.textContent = isSpeaking ? 'Speaking...' : 'Speak';
}

socket.on('connect', () => {
    setConnectionStatus('on');
    setSpeaking(false);
    statusText.textContent = 'Ready to speak your message.';
    errorContainer.style.display = 'none';
});

socket.on('disconnect', () => {
    setConnectionStatus('error');
    setSpeaking(false);
    statusText.textContent = 'Connection lost.';
    errorContainer.textContent = 'Check your UNO Q connection and try again.';
    errorContainer.style.display = 'block';
});

socket.on('speak_status', (message) => {
    errorContainer.style.display = 'none';

    if (message.state === 'speaking') {
        setConnectionStatus('speaking');
        setSpeaking(true);
        statusText.textContent = message.message;
    } else if (message.state === 'error') {
        setConnectionStatus('on');
        setSpeaking(false);
        statusText.textContent = 'Ready to try again.';
        errorContainer.textContent = message.message;
        errorContainer.style.display = 'block';
    } else {
        setConnectionStatus('on');
        setSpeaking(false);
        statusText.textContent = message.message;
    }
});

speakButton.addEventListener('click', () => {
    const text = messageInput.value.trim();

    if (!text) {
        errorContainer.textContent = 'Please enter a message.';
        errorContainer.style.display = 'block';
        return;
    }

    errorContainer.style.display = 'none';
    socket.emit('speak_message', { text });
});

messageInput.addEventListener('input', updateCharacterCount);

messageInput.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        speakButton.click();
    }
});

updateCharacterCount();
