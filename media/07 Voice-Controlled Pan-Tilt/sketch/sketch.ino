/*
 * Lesson 7: Voice-Controlled Pan-Tilt
 *
 * Hold the button connected to D2 and speak a command. Python performs
 * speech recognition and calls one of the Bridge functions below.
 *
 * Pan servo:  P0
 * Tilt servo: P1
 * Button:     D2 to GND
 */

#include <Arduino_RouterBridge.h>
#include "RobotShield.h"

const int BUTTON_PIN = 2;

const int LEFT_ANGLE = -45;
const int RIGHT_ANGLE = 45;
const int UP_ANGLE = -45;
const int DOWN_ANGLE = 45;
const int CENTER_ANGLE = 0;

Servo panServo(0);
Servo tiltServo(1);

int buttonRead(String dummy)
{
    (void)dummy;
    return digitalRead(BUTTON_PIN) == LOW ? 1 : 0;
}

int panLeft(String dummy)
{
    (void)dummy;
    panServo.setAngle(LEFT_ANGLE);
    return LEFT_ANGLE;
}

int panRight(String dummy)
{
    (void)dummy;
    panServo.setAngle(RIGHT_ANGLE);
    return RIGHT_ANGLE;
}

int tiltUp(String dummy)
{
    (void)dummy;
    tiltServo.setAngle(UP_ANGLE);
    return UP_ANGLE;
}

int tiltDown(String dummy)
{
    (void)dummy;
    tiltServo.setAngle(DOWN_ANGLE);
    return DOWN_ANGLE;
}

int centerPanTilt(String dummy)
{
    (void)dummy;
    panServo.setAngle(CENTER_ANGLE);
    tiltServo.setAngle(CENTER_ANGLE);
    return CENTER_ANGLE;
}

void setup()
{
    pinMode(BUTTON_PIN, INPUT_PULLUP);

    I2cBus::i2c().begin();
    panServo.begin();
    tiltServo.begin();

    panServo.setAngle(CENTER_ANGLE);
    tiltServo.setAngle(CENTER_ANGLE);

    Bridge.begin();
    Bridge.provide("button_read", buttonRead);
    Bridge.provide("pan_left", panLeft);
    Bridge.provide("pan_right", panRight);
    Bridge.provide("tilt_up", tiltUp);
    Bridge.provide("tilt_down", tiltDown);
    Bridge.provide("center", centerPanTilt);
}

void loop()
{
    delay(10);
}
