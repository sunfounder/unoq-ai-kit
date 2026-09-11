/*
 * Opposite Reaction Game
 *
 * Rules:
 * - When the matrix shows a LEFT arrow, press the RIGHT button.
 * - When the matrix shows a RIGHT arrow, press the LEFT button.
 * - A correct answer makes a short beep and starts the next round.
 * - A wrong answer shows an X and keeps the buzzer sounding.
 * - Press either button to restart after a wrong answer.
 */

#include <Arduino_LED_Matrix.h>
#include "matrix_patterns.h"

const int LEFT_BUTTON_PIN = 7;
const int RIGHT_BUTTON_PIN = 6;
const int BUZZER_PIN = 5;

const int CORRECT_TONE = 1200;
const int WRONG_TONE = 350;

Arduino_LED_Matrix matrix;

enum Direction {
    LEFT,
    RIGHT
};

Direction currentArrow;
bool gameOver = false;

void showPattern(uint8_t pattern[8][13]) {
    matrix.renderBitmap(pattern, 8, 13);
}

void waitForButtonRelease() {
    while (digitalRead(LEFT_BUTTON_PIN) == LOW ||
           digitalRead(RIGHT_BUTTON_PIN) == LOW) {
        delay(10);
    }
    delay(50);
}

void startRound() {
    currentArrow = random(0, 2) == 0 ? LEFT : RIGHT;

    if (currentArrow == LEFT) {
        showPattern(LEFT_ARROW);
    } else {
        showPattern(RIGHT_ARROW);
    }
}

void correctAnswer() {
    showPattern(CHECK_MARK);

    tone(BUZZER_PIN, CORRECT_TONE);
    delay(120);
    noTone(BUZZER_PIN);

    delay(380);
    startRound();
}

void wrongAnswer() {
    gameOver = true;
    showPattern(CROSS_MARK);
    tone(BUZZER_PIN, WRONG_TONE);
}

void checkAnswer(Direction buttonPressed) {
    bool correct =
        (currentArrow == LEFT && buttonPressed == RIGHT) ||
        (currentArrow == RIGHT && buttonPressed == LEFT);

    if (correct) {
        correctAnswer();
    } else {
        wrongAnswer();
    }
}

void restartGame() {
    noTone(BUZZER_PIN);
    gameOver = false;

    showPattern(SMILE);
    delay(700);

    waitForButtonRelease();
    startRound();
}

void setup() {
    pinMode(LEFT_BUTTON_PIN, INPUT_PULLUP);
    pinMode(RIGHT_BUTTON_PIN, INPUT_PULLUP);
    pinMode(BUZZER_PIN, OUTPUT);

    matrix.begin();
    matrix.clear();

    randomSeed(micros());

    showPattern(SMILE);
    delay(1000);

    startRound();
}

void loop() {
    bool leftPressed = digitalRead(LEFT_BUTTON_PIN) == LOW;
    bool rightPressed = digitalRead(RIGHT_BUTTON_PIN) == LOW;

    if (gameOver) {
        if (leftPressed || rightPressed) {
            waitForButtonRelease();
            restartGame();
        }
        return;
    }

    if (leftPressed) {
        waitForButtonRelease();
        checkAnswer(LEFT);
    } else if (rightPressed) {
        waitForButtonRelease();
        checkAnswer(RIGHT);
    }
}
