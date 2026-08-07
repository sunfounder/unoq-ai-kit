/*
 * AI Voice Vision Assistant V7
 *
 * External LED:
 *   Anode   -> D5 through a current-limiting resistor
 *   Cathode -> GND
 *
 * The LED is controlled only by voice commands interpreted in Python.
 */

#include <Arduino_RouterBridge.h>

constexpr int LED_PIN = 5;

void set_led(int state) {
    digitalWrite(LED_PIN, state ? HIGH : LOW);
}

void setup() {
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);

    Bridge.begin();
    Bridge.provide("set_led", set_led);
}

void loop() {
    delay(50);
}
