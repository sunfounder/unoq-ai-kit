/*
 * AI Rock Paper Scissors
 *
 * RGB LED (common cathode): D8=Red, D7=Green, D6=Blue
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


void ready()
{
    setRgb(0, 0, 0);
    noTone(BUZZER_PIN);
}


void roundStart()
{
    tone(BUZZER_PIN, 1200, 100);
}


void showResult(int result)
{
    noTone(BUZZER_PIN);

    if (result == 1)
    {
        // Player wins: green light and rising notes.
        setRgb(0, 255, 0);
        tone(BUZZER_PIN, 1100, 100);
        delay(130);
        tone(BUZZER_PIN, 1500, 180);
    }
    else if (result == 2)
    {
        // Computer wins: red light and a low note.
        setRgb(255, 0, 0);
        tone(BUZZER_PIN, 500, 300);
    }
    else
    {
        // Tie: blue light and two equal notes.
        setRgb(0, 0, 255);
        tone(BUZZER_PIN, 850, 100);
        delay(140);
        tone(BUZZER_PIN, 850, 100);
    }
}


void setup()
{
    pinMode(RED_PIN, OUTPUT);
    pinMode(GREEN_PIN, OUTPUT);
    pinMode(BLUE_PIN, OUTPUT);
    pinMode(BUZZER_PIN, OUTPUT);
    ready();

    Bridge.begin();
    Bridge.provide("ready", ready);
    Bridge.provide("round_start", roundStart);
    Bridge.provide("show_result", showResult);
}


void loop()
{
    delay(10);
}
