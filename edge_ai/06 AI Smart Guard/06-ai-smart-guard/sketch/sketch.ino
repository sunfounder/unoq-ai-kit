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
 *   D9 = pan servo, D10 = tilt servo
 *   D8=R, D7=G, D6=B  (RGB LED)
 *   D5 = active buzzer
 */

#include <Arduino_RouterBridge.h>
#include <Arduino_HardwareServo.h>

HardwareServo panServo;
HardwareServo tiltServo;

const int RED_LED_PIN = 8;
const int GREEN_LED_PIN = 7;
const int BLUE_LED_PIN = 6;
const int BUZZER_PIN = 5;
const int PAN_SERVO_PIN = 9;
const int TILT_SERVO_PIN = 10;

const int MIN_PAN_ANGLE = 45;
const int MAX_PAN_ANGLE = 135;
const int CENTER_ANGLE = 90;
const int SCAN_STEP = 1;
const unsigned long scanInterval = 40;

int panAngle = CENTER_ANGLE, scanDir = 1;
bool scanning = true, alarming = false;
unsigned long lastScan = 0, lastBeep = 0;
bool beepState = false;

void setRgb(int red, int green, int blue) {
    analogWrite(RED_LED_PIN, red);
    analogWrite(GREEN_LED_PIN, green);
    analogWrite(BLUE_LED_PIN, blue);
}

// ---- Bridge commands ----

void alarm_on() {
    if (alarming) return;
    alarming = true;
    scanning = false;

    // Red LED
    setRgb(255, 0, 0);
}

void alarm_off() {
    if (!alarming) return;
    alarming = false;
    scanning = true;
    digitalWrite(BUZZER_PIN, LOW);

    // Green LED (all clear)
    setRgb(0, 255, 0);
}

// ---- Setup ----

void setup() {
    Serial.begin(115200);

    panServo.attach(PAN_SERVO_PIN);
    tiltServo.attach(TILT_SERVO_PIN);
    panServo.write(CENTER_ANGLE);
    tiltServo.write(CENTER_ANGLE);

    pinMode(RED_LED_PIN, OUTPUT);
    pinMode(GREEN_LED_PIN, OUTPUT);
    pinMode(BLUE_LED_PIN, OUTPUT);
    pinMode(BUZZER_PIN, OUTPUT);
    digitalWrite(BUZZER_PIN, LOW);

    // Start with green (all clear)
    setRgb(0, 255, 0);

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
            digitalWrite(BUZZER_PIN, beepState ? HIGH : LOW);
        }
        return;
    }

    // Scanning mode
    if (!scanning) { delay(20); return; }

    unsigned long now = millis();
    if (now - lastScan < scanInterval) return;
    lastScan = now;

    panAngle += scanDir * SCAN_STEP;
    if (panAngle >= MAX_PAN_ANGLE) {
        panAngle = MAX_PAN_ANGLE;
        scanDir = -1;
    }
    else if (panAngle <= MIN_PAN_ANGLE) {
        panAngle = MIN_PAN_ANGLE;
        scanDir = 1;
    }

    panServo.write(panAngle);
}
