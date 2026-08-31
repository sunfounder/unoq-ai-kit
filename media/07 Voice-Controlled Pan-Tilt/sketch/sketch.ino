/*
 * Voice-Controlled Pan-Tilt
 *
 * Hold the button connected to D2 and speak a command. Python performs
 * speech recognition and calls one of the Bridge functions below.
 *
 * Pan servo:  D9
 * Tilt servo: D10
 * Button:     D2 to GND
 */

#include <Arduino_RouterBridge.h>
#include <Arduino_HardwareServo.h>

const int BUTTON_PIN = 2;

// Servo offsets from the 90° center position
const int LEFT_ANGLE = -45;
const int RIGHT_ANGLE = 45;
const int UP_ANGLE = -45;
const int DOWN_ANGLE = 45;
const int CENTER_ANGLE = 0;

HardwareServo panServo;
HardwareServo tiltServo;

int buttonRead(String dummy)
{
    (void)dummy;
    return digitalRead(BUTTON_PIN) == LOW ? 1 : 0;
}

int panLeft(String dummy)
{
    (void)dummy;
    panServo.write(90 + LEFT_ANGLE);
    return LEFT_ANGLE;
}

int panRight(String dummy)
{
    (void)dummy;
    panServo.write(90 + RIGHT_ANGLE);
    return RIGHT_ANGLE;
}

int tiltUp(String dummy)
{
    (void)dummy;
    tiltServo.write(90 + UP_ANGLE);
    return UP_ANGLE;
}

int tiltDown(String dummy)
{
    (void)dummy;
    tiltServo.write(90 + DOWN_ANGLE);
    return DOWN_ANGLE;
}

int centerPanTilt(String dummy)
{
    (void)dummy;
    panServo.write(90 + CENTER_ANGLE);
    tiltServo.write(90 + CENTER_ANGLE);
    return CENTER_ANGLE;
}

void setup()
{
    pinMode(BUTTON_PIN, INPUT_PULLUP);

    panServo.attach(9);
    tiltServo.attach(10);

    panServo.write(90 + CENTER_ANGLE);
    tiltServo.write(90 + CENTER_ANGLE);

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
