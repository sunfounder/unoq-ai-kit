// SPDX-License-Identifier: MPL-2.0

const socket = io(`http://${window.location.host}`);
const streamUrl = `http://${window.location.hostname}:4912/embed`;

const iframe = document.getElementById('camera-stream');
const placeholder = document.getElementById('video-placeholder');
const statusDot = document.getElementById('status-dot');
const statusLabel = document.getElementById('status-label');
const errorContainer = document.getElementById('error-container');

const MOVE_VIEW = {
    rock: ['✊', 'ROCK'],
    paper: ['✋', 'PAPER'],
    scissors: ['✌️', 'SCISSORS'],
    none: ['—', 'NONE'],
};

const PHASE_VIEW = {
    waiting_start: 'READY',
    starting_round: 'STARTING ROUND',
    countdown: 'GET READY',
    waiting_move: 'SHOW YOUR MOVE',
    resolving: 'CHECKING MOVE',
    result: 'ROUND COMPLETE',
};

let streamLoaded = false;
let reloadTimer;

function setConnection(state, label) {
    statusDot.className = `status-indicator ${state}`;
    statusLabel.textContent = label;
}

function loadStream() {
    if (!streamLoaded) iframe.src = streamUrl;
}

iframe.addEventListener('load', () => {
    streamLoaded = true;
    clearInterval(reloadTimer);
    placeholder.style.display = 'none';
    iframe.style.display = 'block';
    setConnection('on', 'CONNECTED');
});

function setChoice(prefix, move) {
    const view = MOVE_VIEW[move] || ['—', 'WAITING'];
    document.getElementById(`${prefix}-icon`).textContent = view[0];
    document.getElementById(`${prefix}-move`).textContent = view[1];
}

function renderGame(data) {
    const gesture = MOVE_VIEW[data.gesture] || MOVE_VIEW.none;
    document.getElementById('live-gesture').textContent = gesture[1];
    document.getElementById('live-confidence').textContent = `${data.confidence || 0}%`;
    document.getElementById('phase-label').textContent = PHASE_VIEW[data.phase] || 'READY';
    document.getElementById('game-message').textContent = data.message || '';

    const countdown = document.getElementById('countdown');
    if (data.phase === 'countdown' && data.countdown) {
        countdown.hidden = false;
        countdown.textContent = data.countdown;
        countdown.classList.remove('pop');
        void countdown.offsetWidth;
        countdown.classList.add('pop');
    } else {
        countdown.hidden = true;
    }

    setChoice('player', data.player_move);
    setChoice('computer', data.computer_move);

    const banner = document.getElementById('result-banner');
    banner.className = 'result-banner';
    if (data.result === 'win') {
        banner.textContent = 'YOU WIN!';
        banner.classList.add('win');
    } else if (data.result === 'lose') {
        banner.textContent = 'COMPUTER WINS';
        banner.classList.add('lose');
    } else if (data.result === 'tie') {
        banner.textContent = 'TIE GAME';
        banner.classList.add('tie');
    } else if (data.phase === 'waiting_move') {
        banner.textContent = 'HOLD YOUR GESTURE';
    } else {
        banner.textContent = 'PRESS START GAME';
    }

    const startButton = document.getElementById('start-game');
    startButton.disabled = data.phase !== 'waiting_start';

    const scores = data.scores || {};
    document.getElementById('player-score').textContent = scores.player || 0;
    document.getElementById('tie-score').textContent = scores.ties || 0;
    document.getElementById('computer-score').textContent = scores.computer || 0;
}

document.addEventListener('DOMContentLoaded', () => {
    setConnection('', 'CONNECTING');
    loadStream();
    reloadTimer = setInterval(loadStream, 1000);
});

socket.on('connect', () => {
    errorContainer.style.display = 'none';
    socket.emit('get_state', {});
});

socket.on('game_state', renderGame);

socket.on('disconnect', () => {
    setConnection('error', 'DISCONNECTED');
    errorContainer.textContent = 'Connection lost. Check the board and try again.';
    errorContainer.style.display = 'block';
});

document.getElementById('reset-score').addEventListener('click', () => {
    socket.emit('reset_score', {});
});

document.getElementById('start-game').addEventListener('click', () => {
    socket.emit('start_round', {});
});
