/*
 * Lesson 8: Camera Snapshot
 *
 * Wiring:
 *   Button pin 1 -> D2
 *   Button pin 2 -> GND
 *
 * INPUT_PULLUP keeps D2 HIGH while released.
 * Pressing the button connects D2 to GND, so the input becomes LOW.
 */

#include <Arduino_RouterBridge.h>

const int BUTTON_PIN = 2;

int buttonRead(String dummy)
{
    (void)dummy;
    return digitalRead(BUTTON_PIN) == LOW ? 1 : 0;
}

void setup()
{
    pinMode(BUTTON_PIN, INPUT_PULLUP);

    Bridge.begin();
    Bridge.provide("button_read", buttonRead);
}

void loop()
{
    delay(10);
}
