/*
 * AI Object Color Light
 *
 * The Linux application detects an object and sends a color code
 * to this sketch through Router Bridge.
 *
 * RGB LED connections:
 * R -> P6
 * G -> P5
 * B -> P4
 */

#include "RobotShield.h"
#include <Arduino_RouterBridge.h>

Pwm redLed(6);
Pwm greenLed(5);
Pwm blueLed(4);

const uint16_t pwmFrequency = 1000;
const uint16_t pwmPeriod = 1000;

void writeRgb(uint16_t red, uint16_t green, uint16_t blue) {
    redLed.setPulse(red);
    greenLed.setPulse(green);
    blueLed.setPulse(blue);
}

void setColor(int colorCode) {
    switch (colorCode) {
        case 1:  // Red
            writeRgb(1000, 0, 0);
            break;

        case 2:  // Yellow
            writeRgb(1000, 700, 0);
            break;

        case 3:  // Orange
            writeRgb(1000, 250, 0);
            break;

        case 4:  // Green
            writeRgb(0, 1000, 0);
            break;

        case 5:  // Blue
            writeRgb(0, 0, 1000);
            break;

        case 6:  // White
            writeRgb(1000, 1000, 1000);
            break;

        default:  // Off
            writeRgb(0, 0, 0);
            break;
    }
}

void setup() {
    I2cBus::i2c().begin();

    redLed.begin();
    greenLed.begin();
    blueLed.begin();

    redLed.setFreq(pwmFrequency);
    greenLed.setFreq(pwmFrequency);
    blueLed.setFreq(pwmFrequency);

    redLed.setEnable(true);
    greenLed.setEnable(true);
    blueLed.setEnable(true);

    setColor(0);

    Bridge.begin();
    Bridge.provide("set_color", setColor);
}

void loop() {
    delay(20);
}
