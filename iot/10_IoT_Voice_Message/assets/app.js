const recordButton = document.getElementById('record-button');
const playButton = document.getElementById('play-button');
const statusDot = document.getElementById('status-dot');
const statusLabel = document.getElementById('status-label');
const statusText = document.getElementById('status-text');
const errorContainer = document.getElementById('error-container');
const timer = document.getElementById('timer');
const waveform = document.getElementById('waveform');

const socket = io(`http://${window.location.host}`);
const bars = [];
let recording = false;
let playing = false;
let levels = new Array(32).fill(0.02);

for (let i = 0; i < levels.length; i++) {
    const bar = document.createElement('span');
    bar.className = 'wave-bar';
    waveform.appendChild(bar);
    bars.push(bar);
}

function drawWave(level) {
    levels.shift();
    levels.push(Math.max(0.02, Math.min(1, Number(level) || 0)));
    bars.forEach((bar, i) => {
        const shaped = Math.pow(levels[i], 0.65);
        bar.style.height = `${6 + shaped * 92}px`;
    });
}

function resetWave() {
    levels = new Array(32).fill(0.02);
    bars.forEach(bar => bar.style.height = '6px');
}

function formatTime(seconds) {
    seconds = Math.max(0, Number(seconds) || 0);
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    const tenths = Math.floor((seconds % 1) * 10);
    return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}.${tenths}`;
}

function setState(state, hasRecording = playButton.dataset.ready === 'true') {
    recording = state === 'recording';
    playing = state === 'playing';
    const paused = state === 'paused';
    statusDot.className = `status-indicator ${recording ? 'recording' : playing ? 'playing' : 'on'}`;
    statusLabel.textContent = recording ? 'Recording' : playing ? 'Playing' : paused ? 'Paused' : 'Connected';
    recordButton.textContent = recording ? 'Stop' : 'Record';
    recordButton.classList.toggle('recording', recording);
    recordButton.disabled = playing || paused;
    playButton.disabled = recording || !hasRecording;
    playButton.textContent = playing ? 'Pause' : 'Play';
    playButton.dataset.ready = hasRecording ? 'true' : 'false';
}

socket.on('connect', () => {
    statusDot.className = 'status-indicator on';
    statusLabel.textContent = 'Connected';
    statusText.textContent = 'Click Record, then speak toward the UNO Q microphone.';
    errorContainer.style.display = 'none';
});

socket.on('disconnect', () => {
    statusDot.className = 'status-indicator error';
    statusLabel.textContent = 'Disconnected';
    recordButton.disabled = true;
    playButton.disabled = true;
    statusText.textContent = 'Connection lost.';
});

socket.on('voice_level', message => {
    if (message.state === 'recording') {
        setState('recording', false);
        drawWave(message.level);
        timer.textContent = formatTime(message.duration);
        statusText.textContent = 'Recording... speak toward the microphone.';
    }
});

socket.on('voice_status', message => {
    errorContainer.style.display = 'none';
    const hasRecording = Boolean(message.has_recording);
    setState(message.state || 'ready', hasRecording);

    if (message.duration !== undefined) timer.textContent = formatTime(message.duration);

    if (message.state === 'recording') {
        statusText.textContent = 'Recording... speak toward the microphone.';
    } else if (message.state === 'playing') {
        statusText.textContent = 'Playing your voice message through the UNO Q speaker.';
    } else if (message.state === 'paused') {
        statusText.textContent = 'Playback paused. Click Play to continue.';
    } else if (hasRecording) {
        statusText.textContent = 'Recording saved. Click Play to hear your voice message.';
    } else {
        statusText.textContent = 'Click Record, then speak toward the UNO Q microphone.';
    }
});

socket.on('voice_error', message => {
    setState('ready', playButton.dataset.ready === 'true');
    errorContainer.textContent = message.message || 'Audio error.';
    errorContainer.style.display = 'block';
});

recordButton.addEventListener('click', () => {
    errorContainer.style.display = 'none';
    if (recording) {
        socket.emit('record_stop', {});
    } else {
        resetWave();
        timer.textContent = '00:00.0';
        playButton.dataset.ready = 'false';
        setState('recording', false);
        socket.emit('record_start', {});
    }
});

playButton.addEventListener('click', () => {
    if (playButton.disabled) return;
    if (playing) {
        socket.emit('pause_recording', {});
    } else {
        socket.emit('play_recording', {});
    }
});

resetWave();
