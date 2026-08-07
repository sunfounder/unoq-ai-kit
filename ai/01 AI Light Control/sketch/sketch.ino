/*
 * AI Light Control — RGB LED
 *
 * Bridge command from Python:
 *   set_color(int code) — 1=red 2=green 3=blue 4=yellow 5=white 0=off
 *
 * RGB LED on P6(R), P5(G), P4(B)
 *
 * If colors look wrong (e.g. red shows as purple),
 * change COMMON_ANODE below to true.
 */

#include "RobotShield.h"
#include <Arduino_RouterBridge.h>

Pwm redLed(6), greenLed(5), blueLed(4);

void setRgb(uint16_t r, uint16_t g, uint16_t b) {
    redLed.setPulse(r);
    greenLed.setPulse(g);
    blueLed.setPulse(b);
}

void set_color(int code) {
    switch (code) {
        case 1: setRgb(1000, 0, 0);      break;  // red
        case 2: setRgb(0, 1000, 0);      break;  // green
        case 3: setRgb(0, 0, 1000);      break;  // blue
        case 4: setRgb(1000, 700, 0);    break;  // yellow
        case 5: setRgb(1000, 1000, 1000);break;  // white
        default: setRgb(0, 0, 0);        break;  // off
    }
}

void setup() {
    I2cBus::i2c().begin();

    redLed.begin();   redLed.setFreq(1000);   redLed.setEnable(true);
    greenLed.begin(); greenLed.setFreq(1000); greenLed.setEnable(true);
    blueLed.begin();  blueLed.setFreq(1000);  blueLed.setEnable(true);

    // Self-test: cycle R → G → B one by one
    setRgb(1000, 0, 0);    delay(500);   // Red only
    setRgb(0, 1000, 0);    delay(500);   // Green only
    setRgb(0, 0, 1000);    delay(500);   // Blue only
    setRgb(0, 0, 0);

    Bridge.begin();
    Bridge.provide("set_color", set_color);
}

void loop() { delay(50); }
