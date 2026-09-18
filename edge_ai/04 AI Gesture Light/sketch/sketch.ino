/*
 * AI Gesture Light
 *
 * External LED: D5 through a 220 ohm resistor
 */

#include <Arduino_RouterBridge.h>

const int LED_PIN = 5;


int setLed(int state)
{
    digitalWrite(LED_PIN, state ? HIGH : LOW);
    return state ? 1 : 0;
}


void setup()
{
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);

    Bridge.begin();
    Bridge.provide("set_led", setLed);
}


void loop()
{
    delay(10);
}
