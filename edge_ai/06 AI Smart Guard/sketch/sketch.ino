/*
 * AI Smart Guard
 *
 * Full security system: servo scanning, RGB status, buzzer alarm.
 * All controlled from Python via Bridge:
 *   alarm_on()       → red LED + buzzer + stop scan
 *   alarm_off()      → green LED + buzzer off + resume scan
 *   guard_status()   → Python polls this for current state
 *
 * Hardware:
 *   Servo 0 = pan, Servo 1 = tilt (stays at 0)
 *   P6=R, P5=G, P4=B  (RGB LED)
 *   D5 = active buzzer
 */

#include "RobotShield.h"
#include <Arduino_RouterBridge.h>

Servo panServo(0);
Servo tiltServo(1);

Pwm redLed(6), greenLed(5), blueLed(4);

const int buzzerPin = 5;
const int minPan = -45, maxPan = 45, scanStep = 1;
const unsigned long scanInterval = 40;

int panAngle = 0, scanDir = 1;
bool scanning = true, alarming = false;
unsigned long lastScan = 0, lastBeep = 0;
bool beepState = false;

// ---- Bridge commands ----

void alarm_on() {
    if (alarming) return;
    alarming = true;
    scanning = false;

    // Red LED
    redLed.setPulse(1000);
    greenLed.setPulse(0);
    blueLed.setPulse(0);
}

void alarm_off() {
    if (!alarming) return;
    alarming = false;
    scanning = true;
    digitalWrite(buzzerPin, LOW);

    // Green LED (all clear)
    redLed.setPulse(0);
    greenLed.setPulse(1000);
    blueLed.setPulse(0);
}

// ---- Setup ----

void setup() {
    Serial.begin(115200);

    I2cBus::i2c().begin();

    panServo.begin();   panServo.setAngle(0);
    tiltServo.begin();  tiltServo.setAngle(0);

    redLed.begin();    redLed.setFreq(1000);    redLed.setEnable(true);
    greenLed.begin();  greenLed.setFreq(1000);  greenLed.setEnable(true);
    blueLed.begin();   blueLed.setFreq(1000);   blueLed.setEnable(true);

    pinMode(buzzerPin, OUTPUT);
    digitalWrite(buzzerPin, LOW);

    // Start with green (all clear)
    redLed.setPulse(0);
    greenLed.setPulse(1000);
    blueLed.setPulse(0);

    Bridge.begin();
    Bridge.provide("alarm_on", alarm_on);
    Bridge.provide("alarm_off", alarm_off);

    Serial.println("=== AI Smart Guard Ready ===");
}

// ---- Loop ----

void loop() {
    if (alarming) {
        // Beep pattern: 150ms on / 150ms off
        unsigned long now = millis();
        if (now - lastBeep >= 150) {
            lastBeep = now;
            beepState = !beepState;
            digitalWrite(buzzerPin, beepState ? HIGH : LOW);
        }
        return;
    }

    // Scanning mode
    if (!scanning) { delay(20); return; }

    unsigned long now = millis();
    if (now - lastScan < scanInterval) return;
    lastScan = now;

    panAngle += scanDir * scanStep;
    if (panAngle >= maxPan) { panAngle = maxPan; scanDir = -1; }
    else if (panAngle <= minPan) { panAngle = minPan; scanDir = 1; }

    panServo.setAngle(panAngle);
}
