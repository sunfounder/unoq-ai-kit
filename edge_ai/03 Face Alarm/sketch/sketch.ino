/*
 * Face Alarm
 *
 * Bridge commands from Python:
 *   alarm_on()  → starts beeping
 *   alarm_off() → stops
 *
 * Pattern: short beeps repeating while alarm is active.
 */

#include <Arduino_RouterBridge.h>

const int buzzerPin = 5;

bool alarmActive = false;

void alarm_on()  { alarmActive = true; }
void alarm_off() { alarmActive = false; digitalWrite(buzzerPin, LOW); }

void setup() {
    pinMode(buzzerPin, OUTPUT);
    digitalWrite(buzzerPin, LOW);

    Bridge.begin();
    Bridge.provide("alarm_on", alarm_on);
    Bridge.provide("alarm_off", alarm_off);
}

void loop() {
    if (!alarmActive) {
        delay(100);
        return;
    }

    // Rapid beep pattern
    digitalWrite(buzzerPin, HIGH);
    delay(150);
    digitalWrite(buzzerPin, LOW);
    delay(150);
}
