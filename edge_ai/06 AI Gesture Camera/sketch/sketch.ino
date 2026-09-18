/*
 * AI Gesture Camera
 *
 * Pan servo: D9
 * Tilt servo: D10
 */

#include <Arduino_RouterBridge.h>
#include <Arduino_HardwareServo.h>

const int PAN_SERVO_PIN = 9;
const int TILT_SERVO_PIN = 10;

const int PAN_CENTER_ANGLE = 90;
const int TILT_CENTER_ANGLE = 85;
const int TILT_MIN_ANGLE = 60;
const int TILT_MAX_ANGLE = 110;
const int TILT_STEP = 5;

HardwareServo panServo;
HardwareServo tiltServo;
int tiltAngle = TILT_CENTER_ANGLE;


int tiltUp(String dummy)
{
    (void)dummy;
    tiltAngle = constrain(tiltAngle - TILT_STEP, TILT_MIN_ANGLE, TILT_MAX_ANGLE);
    tiltServo.write(tiltAngle);
    return tiltAngle;
}


int tiltDown(String dummy)
{
    (void)dummy;
    tiltAngle = constrain(tiltAngle + TILT_STEP, TILT_MIN_ANGLE, TILT_MAX_ANGLE);
    tiltServo.write(tiltAngle);
    return tiltAngle;
}


int centerPanTilt(String dummy)
{
    (void)dummy;
    panServo.write(PAN_CENTER_ANGLE);
    delay(150);
    tiltAngle = TILT_CENTER_ANGLE;
    tiltServo.write(tiltAngle);
    return 1;
}


void setup()
{
    panServo.attach(PAN_SERVO_PIN);
    tiltServo.attach(TILT_SERVO_PIN);
    panServo.write(PAN_CENTER_ANGLE);
    delay(150);
    tiltServo.write(TILT_CENTER_ANGLE);

    Bridge.begin();
    Bridge.provide("tilt_up", tiltUp);
    Bridge.provide("tilt_down", tiltDown);
    Bridge.provide("center_pan_tilt", centerPanTilt);
}


void loop()
{
    delay(10);
}
