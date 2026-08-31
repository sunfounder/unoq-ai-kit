const socket = io(`http://${window.location.host}`);

const lightValue = document.getElementById('light-value');
const levelFill = document.getElementById('level-fill');
const statusDot = document.getElementById('status-dot');
const statusLabel = document.getElementById('status-label');
const errorContainer = document.getElementById('error-container');
const canvas = document.getElementById('light-chart');
const ctx = canvas.getContext('2d');

const MAX_POINTS = 150;
const samples = [];

function setConnectionStatus(connected) {
    if (connected) {
        statusDot.className = 'status-indicator on';
        statusLabel.textContent = 'Connected';
        errorContainer.style.display = 'none';
        errorContainer.textContent = '';
    } else {
        statusDot.className = 'status-indicator error';
        statusLabel.textContent = 'Disconnected';
        errorContainer.textContent =
            'Connection lost. Check the board and restart the App if needed.';
        errorContainer.style.display = 'block';
    }
}

function addSample(value) {
    samples.push({
        time: performance.now(),
        value: value
    });

    if (samples.length > MAX_POINTS) {
        samples.shift();
    }

    lightValue.textContent = value;
    levelFill.style.width = `${value}%`;

    drawChart();
}

function resizeCanvas() {
    const rect = canvas.getBoundingClientRect();
    const ratio = window.devicePixelRatio || 1;

    canvas.width = Math.round(rect.width * ratio);
    canvas.height = Math.round(rect.height * ratio);

    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    drawChart();
}

function drawChart() {
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;

    if (width <= 0 || height <= 0) {
        return;
    }

    ctx.clearRect(0, 0, width, height);

    const p = {
        left: 42,
        right: 14,
        top: 12,
        bottom: 28
    };

    const plotWidth = width - p.left - p.right;
    const plotHeight = height - p.top - p.bottom;

    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, width, height);

    ctx.font =
        '11px -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';

    [0, 25, 50, 75, 100].forEach(value => {
        const y =
            p.top + plotHeight - (value / 100) * plotHeight;

        ctx.strokeStyle = '#e8edef';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(p.left, y);
        ctx.lineTo(width - p.right, y);
        ctx.stroke();

        ctx.fillStyle = '#90a4ae';
        ctx.fillText(`${value}`, p.left - 9, y);
    });

    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillStyle = '#90a4ae';

    [30, 20, 10, 0].forEach((seconds, i) => {
        const x = p.left + (i / 3) * plotWidth;

        ctx.fillText(
            seconds === 0 ? 'Now' : `-${seconds}s`,
            x,
            p.top + plotHeight + 8
        );
    });

    if (samples.length < 2) {
        return;
    }

    const newest = samples[samples.length - 1].time;
    const windowMs = 30000;

    const points = samples.map(sample => {
        const age = newest - sample.time;
        const normalizedX =
            1 - Math.min(windowMs, age) / windowMs;

        return {
            x: p.left + normalizedX * plotWidth,
            y: p.top + plotHeight -
                (sample.value / 100) * plotHeight
        };
    });

    // Soft red area.
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);

    for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i].x, points[i].y);
    }

    ctx.lineTo(
        points[points.length - 1].x,
        p.top + plotHeight
    );
    ctx.lineTo(points[0].x, p.top + plotHeight);
    ctx.closePath();

    const gradient = ctx.createLinearGradient(
        0,
        p.top,
        0,
        p.top + plotHeight
    );

    gradient.addColorStop(0, 'rgba(229, 57, 53, 0.16)');
    gradient.addColorStop(1, 'rgba(229, 57, 53, 0.01)');

    ctx.fillStyle = gradient;
    ctx.fill();

    // Main red trend line.
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);

    for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i].x, points[i].y);
    }

    ctx.strokeStyle = '#e53935';
    ctx.lineWidth = 2.5;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.stroke();

    const last = points[points.length - 1];

    ctx.beginPath();
    ctx.arc(last.x, last.y, 4, 0, Math.PI * 2);
    ctx.fillStyle = '#e53935';
    ctx.fill();
}

socket.on('connect', () => {
    setConnectionStatus(true);
});

socket.on('disconnect', () => {
    setConnectionStatus(false);
});

socket.on('light_level', message => {
    if (!message || typeof message.value === 'undefined') {
        return;
    }

    const value = Math.max(
        0,
        Math.min(100, Number(message.value))
    );

    addSample(Math.round(value));
});

window.addEventListener('resize', resizeCanvas);

resizeCanvas();
