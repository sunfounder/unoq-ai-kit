/*
 * Voice-Controlled RGB LED
 *
 * Wiring:
 *   Push button: D2 -> GND
 *   RGB LED R:   220Ω -> D8
 *   RGB LED G:   220Ω -> D7
 *   RGB LED B:   220Ω -> D6
 */

#include <Arduino_RouterBridge.h>

const int BUTTON_PIN = 2;

const int RED_PIN = 8;
const int GREEN_PIN = 7;
const int BLUE_PIN = 6;

void setRgb(int red, int green, int blue)
{
    analogWrite(RED_PIN, red);
    analogWrite(GREEN_PIN, green);
    analogWrite(BLUE_PIN, blue);
}

void setColor(String color)
{
    String selectedColor = color;
    selectedColor.toLowerCase();

    if (selectedColor == "red") {
        setRgb(255, 0, 0);
    } else if (selectedColor == "green") {
        setRgb(0, 255, 0);
    } else if (selectedColor == "blue") {
        setRgb(0, 0, 255);
    } else if (selectedColor == "yellow") {
        setRgb(255, 180, 0);
    } else if (selectedColor == "cyan") {
        setRgb(0, 255, 255);
    } else if (selectedColor == "purple") {
        setRgb(128, 0, 180);
    } else if (selectedColor == "white") {
        setRgb(255, 255, 255);
    } else {
        setRgb(0, 0, 0);
    }
}

int buttonRead(String dummy)
{
    (void)dummy;
    return digitalRead(BUTTON_PIN) == LOW ? 1 : 0;
}

void setup()
{
    pinMode(BUTTON_PIN, INPUT_PULLUP);

    pinMode(RED_PIN, OUTPUT);
    pinMode(GREEN_PIN, OUTPUT);
    pinMode(BLUE_PIN, OUTPUT);

    // Startup test: red -> green -> blue.
    setRgb(255, 0, 0);
    delay(500);
    setRgb(0, 255, 0);
    delay(500);
    setRgb(0, 0, 255);
    delay(500);
    setRgb(0, 0, 0);

    Bridge.begin();
    Bridge.provide("button_read", buttonRead);
    Bridge.provide("set_color", setColor);
}

void loop()
{
    delay(10);
}
