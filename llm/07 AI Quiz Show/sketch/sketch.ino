/*
 * 07 AI Quiz Show
 *
 * Passive buzzer: D5
 * RGB LED: D8 (red), D7 (green), D6 (blue)
 */

#include <Arduino_RouterBridge.h>

const int BUZZER_PIN = 5;
const int BLUE_PIN = 6;
const int GREEN_PIN = 7;
const int RED_PIN = 8;

void setRgb(int red, int green, int blue)
{
    analogWrite(RED_PIN, red);
    analogWrite(GREEN_PIN, green);
    analogWrite(BLUE_PIN, blue);
}

void correctSound()
{
    tone(BUZZER_PIN, 880, 100);
    delay(130);
    tone(BUZZER_PIN, 1175, 160);
}

void wrongSound()
{
    tone(BUZZER_PIN, 330, 250);
}

void quiz_feedback(int code)
{
    switch (code) {
        case 1:
            setRgb(255, 160, 0);  // Yellow: waiting for an answer
            break;
        case 2:
            setRgb(0, 255, 0);    // Green: correct
            correctSound();
            break;
        case 3:
            setRgb(255, 0, 0);    // Red: wrong or error
            wrongSound();
            break;
        default:
            setRgb(0, 0, 0);
            noTone(BUZZER_PIN);
            break;
    }
}

void setup()
{
    pinMode(BUZZER_PIN, OUTPUT);
    pinMode(RED_PIN, OUTPUT);
    pinMode(GREEN_PIN, OUTPUT);
    pinMode(BLUE_PIN, OUTPUT);

    setRgb(0, 0, 0);

    Bridge.begin();
    Bridge.provide("quiz_feedback", quiz_feedback);
}

void loop()
{
    delay(10);
}
