/*
 * 03 Voice Recorder
 *
 * Wiring:
 *   Record button: D7 -> button -> GND
 *   Play button:   D6 -> button -> GND
 *
 * Both pins use INPUT_PULLUP:
 *   released = HIGH
 *   pressed  = LOW
 */

#include <Arduino_RouterBridge.h>

const int RECORD_BUTTON_PIN = 7;
const int PLAY_BUTTON_PIN = 6;

int recordButtonRead(String dummy)
{
    (void)dummy;
    return digitalRead(RECORD_BUTTON_PIN) == LOW ? 1 : 0;
}

int playButtonRead(String dummy)
{
    (void)dummy;
    return digitalRead(PLAY_BUTTON_PIN) == LOW ? 1 : 0;
}

void setup()
{
    pinMode(RECORD_BUTTON_PIN, INPUT_PULLUP);
    pinMode(PLAY_BUTTON_PIN, INPUT_PULLUP);

    Bridge.begin();

    // The Linux/Python side reads the two button states through Bridge.call().
    Bridge.provide("record_button_read", recordButtonRead);
    Bridge.provide("play_button_read", playButtonRead);
}

void loop()
{
    delay(10);
}
