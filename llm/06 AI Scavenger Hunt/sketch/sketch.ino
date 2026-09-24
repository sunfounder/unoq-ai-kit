/*
 * 06 AI Scavenger Hunt
 * RGB LED: D8 (red), D7 (green), D6 (blue)
 * Buzzer: D5
 */

#include <Arduino_RouterBridge.h>

const int RED_PIN = 8;
const int GREEN_PIN = 7;
const int BLUE_PIN = 6;
const int BUZZER_PIN = 5;

void setRgb(int red, int green, int blue)
{
    analogWrite(RED_PIN, red);
    analogWrite(GREEN_PIN, green);
    analogWrite(BLUE_PIN, blue);
}

void successSound()
{
    tone(BUZZER_PIN, 880, 100);
    delay(130);
    tone(BUZZER_PIN, 1175, 160);
}

void failureSound()
{
    tone(BUZZER_PIN, 330, 220);
}

void game_feedback(int code)
{
    switch (code) {
        case 1:
            setRgb(255, 160, 0);  // Yellow: mission active
            break;
        case 2:
            setRgb(0, 255, 0);    // Green: success
            successSound();
            break;
        case 3:
            setRgb(255, 0, 0);    // Red: try again
            failureSound();
            break;
        default:
            setRgb(0, 0, 0);      // Off
            noTone(BUZZER_PIN);
            break;
    }
}

void setup()
{
    pinMode(RED_PIN, OUTPUT);
    pinMode(GREEN_PIN, OUTPUT);
    pinMode(BLUE_PIN, OUTPUT);
    pinMode(BUZZER_PIN, OUTPUT);
    setRgb(0, 0, 0);
    Bridge.begin();
    Bridge.provide("game_feedback", game_feedback);
}

void loop()
{
    delay(20);
}
