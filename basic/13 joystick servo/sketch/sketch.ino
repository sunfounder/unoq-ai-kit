/*
 * Joystick Incremental Servo Control
 * Y axis controls the pan servo on P0.
 * X axis controls the tilt servo on P1.
 * Press the joystick button to reset both servos to 0°.
 */

#include "RobotShield.h"

const int swPin = 2;
const int xPin = A3;
const int yPin = A2;

Servo panServo(0);
Servo tiltServo(1);

int panAngle = 0;
int tiltAngle = 0;

int xCenter = 512;
int yCenter = 512;

const int minAngle = -45;
const int maxAngle = 45;
const int deadZone = 100;
const int stepSize = 1;

void setup() {
    Serial.begin(115200);
    pinMode(swPin, INPUT_PULLUP);

    I2cBus::i2c().begin();
    panServo.begin();
    tiltServo.begin();

    panAngle = 0;
    tiltAngle = 0;

    panServo.setAngle(panAngle);
    tiltServo.setAngle(tiltAngle);

    delay(500);

    long xTotal = 0;
    long yTotal = 0;

    for (int i = 0; i < 20; i++) {
        xTotal += analogRead(xPin);
        yTotal += analogRead(yPin);
        delay(10);
    }

    xCenter = xTotal / 20;
    yCenter = yTotal / 20;

    Serial.println("=== Joystick Servo Control Ready ===");
    Serial.print("X Center: ");
    Serial.println(xCenter);
    Serial.print("Y Center: ");
    Serial.println(yCenter);
}

void loop() {
    if (digitalRead(swPin) == LOW) {
        panAngle = 0;
        tiltAngle = 0;

        panServo.setAngle(panAngle);
        tiltServo.setAngle(tiltAngle);

        Serial.println("Reset both servos to 0 degrees");
        delay(300);
        return;
    }

    int xValue = analogRead(xPin);
    int yValue = analogRead(yPin);

    if (yValue > yCenter + deadZone) {
        panAngle += stepSize;
    } else if (yValue < yCenter - deadZone) {
        panAngle -= stepSize;
    }

    if (xValue > xCenter + deadZone) {
        tiltAngle += stepSize;
    } else if (xValue < xCenter - deadZone) {
        tiltAngle -= stepSize;
    }

    panAngle = constrain(panAngle, minAngle, maxAngle);
    tiltAngle = constrain(tiltAngle, minAngle, maxAngle);

    panServo.setAngle(panAngle);
    tiltServo.setAngle(tiltAngle);

    Serial.print("X: ");
    Serial.print(xValue);
    Serial.print("  Y: ");
    Serial.print(yValue);
    Serial.print("  Pan: ");
    Serial.print(panAngle);
    Serial.print("  Tilt: ");
    Serial.println(tiltAngle);

    delay(30);
}