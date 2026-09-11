/*
 * STT Echo
 *
 * Wiring:
 *   Button pin 1 -> D4
 *   Button pin 2 -> GND
 *
 * INPUT_PULLUP keeps D4 HIGH while released.
 * Pressing the button connects D4 to GND, so the input becomes LOW.
 */

#include <Arduino_RouterBridge.h>

const int BUTTON_PIN = 4;

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
