const socket = io(`http://${window.location.host}`);

const mazeElement = document.getElementById('maze');
const movesElement = document.getElementById('moves');
const timeElement = document.getElementById('time');
const statusDot = document.getElementById('status-dot');
const statusLabel = document.getElementById('status-label');
const statusText = document.getElementById('status-text');
const errorContainer = document.getElementById('error-container');

const restartButton = document.getElementById('restart-button');
const winOverlay = document.getElementById('win-overlay');
const playAgainButton = document.getElementById('play-again-button');
const finalMoves = document.getElementById('final-moves');
const finalTime = document.getElementById('final-time');

// 0 = path, 1 = wall
const layout = [
    [0,0,1,0,0,0,1,0,0,0,0,0,0],
    [1,0,1,0,1,0,1,0,1,1,1,1,0],
    [0,0,0,0,1,0,0,0,0,0,0,1,0],
    [0,1,1,1,1,1,1,0,1,1,0,1,0],
    [0,0,0,0,0,0,0,0,1,0,0,0,0],
    [1,1,1,1,0,1,1,1,1,0,1,1,0],
    [0,0,0,1,0,0,0,0,0,0,1,0,0],
    [0,1,0,1,1,1,1,1,1,0,1,0,1],
    [0,1,0,0,0,0,0,0,0,0,0,0,0]
];

const start = { row: 0, col: 0 };
const goal = { row: 8, col: 12 };

let player = { ...start };
let moves = 0;
let startTime = null;
let timerId = null;
let won = false;

function setConnectionStatus(state) {
    statusDot.className = `status-indicator ${state}`;

    if (state === 'on') {
        statusLabel.textContent = 'Connected';
    } else if (state === 'success') {
        statusLabel.textContent = 'Complete';
    } else if (state === 'error') {
        statusLabel.textContent = 'Disconnected';
    } else {
        statusLabel.textContent = 'Ready';
    }
}

function buildMaze() {
    mazeElement.innerHTML = '';

    layout.forEach((row, r) => {
        row.forEach((value, c) => {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.dataset.row = r;
            cell.dataset.col = c;

            if (value === 1) {
                cell.classList.add('wall');
            }

            mazeElement.appendChild(cell);
        });
    });

    render();
}

function getCell(row, col) {
    return mazeElement.querySelector(
        `.cell[data-row="${row}"][data-col="${col}"]`
    );
}

function render() {
    mazeElement.querySelectorAll('.player').forEach(
        el => el.classList.remove('player')
    );

    mazeElement.querySelectorAll('.goal').forEach(
        el => el.classList.remove('goal')
    );

    const playerCell = getCell(player.row, player.col);
    const goalCell = getCell(goal.row, goal.col);

    goalCell?.classList.add('goal');
    playerCell?.classList.add('player');

    movesElement.textContent = moves;
}

function beginTimer() {
    if (startTime !== null) {
        return;
    }

    startTime = performance.now();

    timerId = setInterval(() => {
        if (!won) {
            const seconds = (performance.now() - startTime) / 1000;
            timeElement.textContent = `${seconds.toFixed(1)} s`;
        }
    }, 100);
}

function move(direction) {
    if (won) {
        return;
    }

    beginTimer();

    const next = { ...player };

    if (direction === 'up') next.row--;
    if (direction === 'down') next.row++;
    if (direction === 'left') next.col--;
    if (direction === 'right') next.col++;

    if (
        next.row < 0 ||
        next.row >= layout.length ||
        next.col < 0 ||
        next.col >= layout[0].length ||
        layout[next.row][next.col] === 1
    ) {
        statusText.textContent = 'That way is blocked. Try another direction.';
        return;
    }

    player = next;
    moves++;

    statusText.textContent = 'Keep going!';
    statusText.classList.remove('success-text');

    render();

    if (player.row === goal.row && player.col === goal.col) {
        winGame();
    }
}

function winGame() {
    won = true;

    if (timerId) {
        clearInterval(timerId);
        timerId = null;
    }

    const seconds = startTime === null
        ? 0
        : (performance.now() - startTime) / 1000;

    timeElement.textContent = `${seconds.toFixed(1)} s`;

    // Keep the player visible on the goal cell.
    render();

    setConnectionStatus('success');
    statusText.textContent = 'Maze complete! You reached the goal.';
    statusText.classList.add('success-text');

    finalMoves.textContent = moves;
    finalTime.textContent = `${seconds.toFixed(1)} s`;

    // Small delay lets the user see the final player position first.
    setTimeout(() => {
        winOverlay.classList.add('show');
        winOverlay.setAttribute('aria-hidden', 'false');
    }, 350);
}

function resetGame() {
    player = { ...start };
    moves = 0;
    won = false;
    startTime = null;

    if (timerId) {
        clearInterval(timerId);
        timerId = null;
    }

    timeElement.textContent = '0.0 s';
    movesElement.textContent = '0';

    statusText.textContent = 'Move the joystick to reach the goal.';
    statusText.classList.remove('success-text');

    winOverlay.classList.remove('show');
    winOverlay.setAttribute('aria-hidden', 'true');

    if (socket.connected) {
        setConnectionStatus('on');
    } else {
        setConnectionStatus('');
    }

    render();
}

socket.on('connect', () => {
    setConnectionStatus('on');
    errorContainer.style.display = 'none';
    errorContainer.textContent = '';
});

socket.on('disconnect', () => {
    setConnectionStatus('error');

    errorContainer.textContent =
        'Connection lost. Check your board and try again.';
    errorContainer.style.display = 'block';
});

socket.on('joystick_move', (message) => {
    if (message && message.direction) {
        move(message.direction);
    }
});

socket.on('reset_game', () => {
    resetGame();
});

restartButton.addEventListener('click', resetGame);
playAgainButton.addEventListener('click', resetGame);

buildMaze();
