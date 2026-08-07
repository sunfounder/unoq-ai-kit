/*
 * Voice-Controlled RGB LED
 *
 * Wiring:
 *   Push button: D2 -> GND
 *   RGB LED R:   P6
 *   RGB LED G:   P5
 *   RGB LED B:   P4
 */

#include "RobotShield.h"
#include <Arduino_RouterBridge.h>

const int BUTTON_PIN = 2;

Pwm redLed(6);
Pwm greenLed(5);
Pwm blueLed(4);

void setRgb(uint16_t red, uint16_t green, uint16_t blue)
{
    redLed.setPulse(red);
    greenLed.setPulse(green);
    blueLed.setPulse(blue);
}

void setColor(String color)
{
    String selectedColor = color;
    selectedColor.toLowerCase();

    if (selectedColor == "red") {
        setRgb(1000, 0, 0);
    } else if (selectedColor == "green") {
        setRgb(0, 1000, 0);
    } else if (selectedColor == "blue") {
        setRgb(0, 0, 1000);
    } else if (selectedColor == "yellow") {
        setRgb(1000, 700, 0);
    } else if (selectedColor == "cyan") {
        setRgb(0, 1000, 1000);
    } else if (selectedColor == "purple") {
        setRgb(500, 0, 700);
    } else if (selectedColor == "white") {
        setRgb(1000, 1000, 1000);
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

    I2cBus::i2c().begin();

    redLed.begin();
    greenLed.begin();
    blueLed.begin();

    redLed.setFreq(1000);
    greenLed.setFreq(1000);
    blueLed.setFreq(1000);

    redLed.setEnable(true);
    greenLed.setEnable(true);
    blueLed.setEnable(true);

    // Startup test: red -> green -> blue.
    setRgb(1000, 0, 0);
    delay(500);
    setRgb(0, 1000, 0);
    delay(500);
    setRgb(0, 0, 1000);
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
