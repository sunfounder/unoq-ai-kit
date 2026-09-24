// SPDX-FileCopyrightText: Copyright (C) SunFounder
// SPDX-License-Identifier: MPL-2.0

const socket = io(`http://${window.location.host}`);

const statusDot = document.getElementById('status-dot');
const connectionLabel = document.getElementById('connection-label');
const statusPanel = document.getElementById('status-panel');
const statusTitle = document.getElementById('status-title');
const statusMessage = document.getElementById('status-message');
const scoreValue = document.getElementById('score-value');
const answeredValue = document.getElementById('answered-value');
const questionText = document.getElementById('question-text');
const choiceA = document.getElementById('choice-a');
const choiceB = document.getElementById('choice-b');
const choiceC = document.getElementById('choice-c');
const choiceButtons = [...document.querySelectorAll('.choice')];
const newButton = document.getElementById('new-button');
const resetButton = document.getElementById('reset-button');
const resultCard = document.getElementById('result-card');
const resultText = document.getElementById('result-text');
const errorContainer = document.getElementById('error-container');

let busy = false;
let hasQuestion = false;
let questionAnswered = false;

const stateTitles = {
    ready: 'Ready',
    generating: 'Creating Question',
    speaking: 'Reading Question',
    correct: 'Correct!',
    wrong: 'Not Quite',
    complete: 'Question Complete',
    error: 'Error',
};

function updateButtons(state) {
    busy = ['generating', 'speaking', 'correct', 'wrong'].includes(state);
    const canAnswer = socket.connected && hasQuestion && !questionAnswered && !busy;

    choiceButtons.forEach((button) => {
        button.disabled = !canAnswer;
    });
    newButton.disabled = busy || !socket.connected;
    resetButton.disabled = busy || !socket.connected;
}

function updateState(data) {
    const state = data.state || 'ready';
    const quiz = data.quiz || null;
    const previousQuestion = hasQuestion ? questionText.textContent : '';

    hasQuestion = Boolean(quiz);
    questionAnswered = Boolean(data.answered);

    if (quiz) {
        questionText.textContent = quiz.question;
        choiceA.textContent = quiz.choices.A;
        choiceB.textContent = quiz.choices.B;
        choiceC.textContent = quiz.choices.C;
    } else {
        questionText.textContent = 'Choose NEW QUESTION to begin.';
        choiceA.textContent = '—';
        choiceB.textContent = '—';
        choiceC.textContent = '—';
    }

    scoreValue.textContent = Number(data.score || 0);
    answeredValue.textContent = Number(data.questions_answered || 0);

    statusPanel.className = `status-panel ${state}`;
    statusTitle.textContent = stateTitles[state] || state;
    statusMessage.textContent = data.message || '';

    choiceButtons.forEach((button) => {
        button.classList.remove('selected', 'correct-choice', 'wrong-choice');
    });

    if (data.selected) {
        const selectedButton = document.querySelector(`[data-answer="${data.selected}"]`);
        if (selectedButton) {
            selectedButton.classList.add(state === 'correct' ? 'correct-choice' : 'wrong-choice');
        }
    }

    const questionChanged = Boolean(quiz && quiz.question !== previousQuestion);
    resultCard.className = `result-card ${state}`;
    if (data.result) {
        resultText.textContent = data.result;
    } else if (state === 'generating') {
        resultText.textContent = 'Waiting for a new question...';
    } else if (questionChanged) {
        resultText.textContent = 'Choose your answer to see the explanation.';
    } else if (!quiz) {
        resultText.textContent = 'The explanation will appear here.';
    }

    if (state === 'error') {
        errorContainer.textContent = data.message || 'Unknown error';
        errorContainer.style.display = 'block';
    } else {
        errorContainer.textContent = '';
        errorContainer.style.display = 'none';
    }

    updateButtons(state);
}

choiceButtons.forEach((button) => {
    button.addEventListener('click', () => {
        if (button.disabled) return;
        choiceButtons.forEach((item) => { item.disabled = true; });
        socket.emit('submit_answer', { answer: button.dataset.answer });
    });
});

newButton.addEventListener('click', () => {
    if (busy || !socket.connected) return;
    updateState({
        state: 'generating',
        message: 'AI is creating a new question...',
        quiz: hasQuestion ? {
            question: questionText.textContent,
            choices: { A: choiceA.textContent, B: choiceB.textContent, C: choiceC.textContent },
        } : null,
        score: scoreValue.textContent,
        questions_answered: answeredValue.textContent,
        answered: questionAnswered,
    });
    socket.emit('new_question', {});
});

resetButton.addEventListener('click', () => {
    if (busy || !socket.connected) return;
    socket.emit('reset_quiz', {});
});

socket.on('connect', () => {
    statusDot.className = 'status-indicator on';
    connectionLabel.textContent = 'Connected';
    socket.emit('get_state', {});
});

socket.on('quiz_state', updateState);

socket.on('disconnect', () => {
    statusDot.className = 'status-indicator error';
    connectionLabel.textContent = 'Disconnected';
    updateState({
        state: 'error',
        message: 'Connection to the app was lost.',
        quiz: null,
        score: scoreValue.textContent,
        questions_answered: answeredValue.textContent,
        answered: true,
    });
});
