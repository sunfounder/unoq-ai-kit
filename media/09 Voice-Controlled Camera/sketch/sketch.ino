/*
 * Voice-Controlled Camera
 *
 * Python recognizes voice commands and calls the Bridge functions below.
 *
 * Pan servo:  D9
 * Tilt servo: D10
 */

#include <Arduino_RouterBridge.h>
#include <Arduino_HardwareServo.h>

// Servo angles
const int LEFT_ANGLE = 135;
const int RIGHT_ANGLE = 45;
const int UP_ANGLE = 45;
const int DOWN_ANGLE = 115;
const int CENTER_ANGLE = 90;

HardwareServo panServo;
HardwareServo tiltServo;

int panLeft(String dummy)
{
    (void)dummy;
    panServo.write(LEFT_ANGLE);
    return LEFT_ANGLE;
}

int panRight(String dummy)
{
    (void)dummy;
    panServo.write(RIGHT_ANGLE);
    return RIGHT_ANGLE;
}

int tiltUp(String dummy)
{
    (void)dummy;
    tiltServo.write(UP_ANGLE);
    return UP_ANGLE;
}

int tiltDown(String dummy)
{
    (void)dummy;
    tiltServo.write(DOWN_ANGLE);
    return DOWN_ANGLE;
}

int centerPanTilt(String dummy)
{
    (void)dummy;
    panServo.write(CENTER_ANGLE);
    tiltServo.write(CENTER_ANGLE);
    return CENTER_ANGLE;
}

void setup()
{
    panServo.attach(9);
    tiltServo.attach(10);

    panServo.write(CENTER_ANGLE);
    tiltServo.write(CENTER_ANGLE);
    delay(500);

    Bridge.begin();
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
