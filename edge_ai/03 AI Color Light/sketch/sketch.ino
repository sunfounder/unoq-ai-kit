/*
 * AI Object Color Light
 *
 * The Linux application detects an object and sends a color code
 * to this sketch through Router Bridge.
 *
 * RGB LED connections:
 * R -> D8
 * G -> D7
 * B -> D6
 */

#include <Arduino_RouterBridge.h>

const int redPin = 8;
const int greenPin = 7;
const int bluePin = 6;

void writeRgb(int red, int green, int blue) {
    analogWrite(redPin, red);
    analogWrite(greenPin, green);
    analogWrite(bluePin, blue);
}

void setColor(int colorCode) {
    switch (colorCode) {
        case 1:  // Red
            writeRgb(255, 0, 0);
            break;

        case 2:  // Yellow
            writeRgb(255, 180, 0);
            break;

        case 3:  // Orange
            writeRgb(255, 64, 0);
            break;

        case 4:  // Green
            writeRgb(0, 255, 0);
            break;

        case 5:  // Blue
            writeRgb(0, 0, 255);
            break;

        case 6:  // White
            writeRgb(255, 255, 255);
            break;

        default:  // Off
            writeRgb(0, 0, 0);
            break;
    }
}

void setup() {
    pinMode(redPin, OUTPUT);
    pinMode(greenPin, OUTPUT);
    pinMode(bluePin, OUTPUT);

    setColor(0);

    Bridge.begin();
    Bridge.provide("set_color", setColor);
}

void loop() {
    delay(20);
}
