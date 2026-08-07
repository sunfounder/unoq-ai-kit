/*
 * Face Tracking Camera
 *
 * The pan servo on P0 scans from left to right.
 * The tilt servo on P1 remains at 0 degrees.
 * When the Linux application detects a face, scanning stops.
 * Scanning resumes when the face is no longer visible.
 */

#include "RobotShield.h"
#include <Arduino_RouterBridge.h>

Servo panServo(0);
Servo tiltServo(1);

const int minPanAngle = -45;
const int maxPanAngle = 45;
const int scanStep = 1;

const unsigned long scanInterval = 40;

int panAngle = 0;
int scanDirection = 1;

bool scanningEnabled = true;
unsigned long previousScanTime = 0;

void stopScanning() {
    scanningEnabled = false;
}

void startScanning() {
    scanningEnabled = true;
}

void setup() {
    Serial.begin(115200);

    I2cBus::i2c().begin();

    panServo.begin();
    tiltServo.begin();

    panServo.setAngle(0);
    tiltServo.setAngle(0);

    Bridge.begin();

    Bridge.provide("stop_scanning", stopScanning);
    Bridge.provide("start_scanning", startScanning);
}

void loop() {
    if (!scanningEnabled) {
        delay(20);
        return;
    }

    unsigned long currentTime = millis();

    if (currentTime - previousScanTime < scanInterval) {
        return;
    }

    previousScanTime = currentTime;

    panAngle += scanDirection * scanStep;

    if (panAngle >= maxPanAngle) {
        panAngle = maxPanAngle;
        scanDirection = -1;
    } else if (panAngle <= minPanAngle) {
        panAngle = minPanAngle;
        scanDirection = 1;
    }

    panServo.setAngle(panAngle);
}
