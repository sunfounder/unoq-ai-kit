/*
 * AI Light Control — RGB LED
 *
 * Bridge command from Python:
 *   set_color(int code) — 1=red 2=green 3=blue 4=yellow 5=white 0=off
 *
 * RGB LED on D8(R), D7(G), D6(B)
 */

#include <Arduino_RouterBridge.h>

const int redPin = 8;
const int greenPin = 7;
const int bluePin = 6;

void setRgb(int r, int g, int b) {
    analogWrite(redPin, r);
    analogWrite(greenPin, g);
    analogWrite(bluePin, b);
}

void set_color(int code) {
    switch (code) {
        case 1: setRgb(255, 0, 0);        break;  // red
        case 2: setRgb(0, 255, 0);        break;  // green
        case 3: setRgb(0, 0, 255);        break;  // blue
        case 4: setRgb(255, 180, 0);      break;  // yellow
        case 5: setRgb(255, 255, 255);    break;  // white
        default: setRgb(0, 0, 0);         break;  // off
    }
}

void setup() {
    pinMode(redPin, OUTPUT);
    pinMode(greenPin, OUTPUT);
    pinMode(bluePin, OUTPUT);

    // Self-test: cycle R → G → B one by one
    setRgb(255, 0, 0);      delay(500);   // Red only
    setRgb(0, 255, 0);      delay(500);   // Green only
    setRgb(0, 0, 255);      delay(500);   // Blue only
    setRgb(0, 0, 0);

    Bridge.begin();
    Bridge.provide("set_color", set_color);
}

void loop() { delay(50); }
