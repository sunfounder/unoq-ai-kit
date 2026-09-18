const temperatureValue = document.getElementById('temperature-value');
const humidityValue = document.getElementById('humidity-value');
const lightValue = document.getElementById('light-value');
const lightLabel = document.getElementById('light-label');
const analysisStatus = document.getElementById('analysis-status');
const analysisSummary = document.getElementById('analysis-summary');
const analysisSuggestion = document.getElementById('analysis-suggestion');
const analyzeButton = document.getElementById('analyze-button');
const statusDot = document.getElementById('status-dot');
const statusLabel = document.getElementById('status-label');
const statusText = document.getElementById('status-text');
const errorContainer = document.getElementById('error-container');

const socket = io(`http://${window.location.host}`);
let hasSensorData = false;
let analyzing = false;

function setConnectionStatus(state) {
    statusDot.className = `status-indicator ${state}`;

    if (state === 'on') statusLabel.textContent = 'Connected';
    else if (state === 'analyzing') statusLabel.textContent = 'Analyzing';
    else if (state === 'error') statusLabel.textContent = 'Disconnected';
    else statusLabel.textContent = 'Ready';
}

function setAnalyzing(value) {
    analyzing = value;
    analyzeButton.disabled = value || !hasSensorData;
    analyzeButton.textContent = value ? 'Analyzing…' : 'Analyze Environment';
}

function showError(message) {
    errorContainer.textContent = message;
    errorContainer.style.display = 'block';
}

socket.on('connect', () => {
    setConnectionStatus('on');
    errorContainer.style.display = 'none';
    socket.emit('request_state', {});
});

socket.on('disconnect', () => {
    setConnectionStatus('error');
    setAnalyzing(false);
    statusText.textContent = 'Connection lost.';
    showError('Check your UNO Q connection and try again.');
});

socket.on('sensor_update', (data) => {
    if (data.temperature === null || data.humidity === null) return;

    hasSensorData = true;
    temperatureValue.textContent = `${Number(data.temperature).toFixed(1)}°C`;
    humidityValue.textContent = `${Number(data.humidity).toFixed(1)}%`;
    lightValue.textContent = `${data.light_percent}%`;
    lightLabel.textContent = data.light_label;

    if (!analyzing) analyzeButton.disabled = false;
    statusText.textContent = 'Live sensor data is updating every two seconds.';
    errorContainer.style.display = 'none';
});

socket.on('sensor_error', (data) => {
    statusText.textContent = 'Sensor reading failed.';
    showError(data.message || 'Check the DHT11 wiring and try again.');
});

socket.on('analysis_status', (data) => {
    if (data.state === 'analyzing') {
        setConnectionStatus('analyzing');
        setAnalyzing(true);
        analysisStatus.textContent = 'Analyzing…';
        analysisSummary.textContent = 'AI is reviewing the current sensor readings.';
        errorContainer.style.display = 'none';
    }
});

socket.on('analysis_result', (data) => {
    setConnectionStatus('on');
    setAnalyzing(false);
    analysisStatus.textContent = data.status;
    analysisSummary.textContent = data.summary;
    analysisSuggestion.textContent = data.suggestion;
    statusText.textContent = 'Analysis complete. Sensor data continues to update.';
});

socket.on('analysis_error', (data) => {
    setConnectionStatus('on');
    setAnalyzing(false);
    analysisStatus.textContent = 'Analysis unavailable';
    analysisSummary.textContent = 'The environment could not be analyzed.';
    statusText.textContent = 'Ready to try again.';
    showError(data.message || 'Please try again.');
});

analyzeButton.addEventListener('click', () => {
    if (!hasSensorData || analyzing) return;
    socket.emit('analyze_environment', {});
});
