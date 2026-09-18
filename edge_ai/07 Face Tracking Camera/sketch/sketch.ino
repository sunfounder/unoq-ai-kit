/*
 * Face Tracking Camera
 *
 * The pan servo on D9 follows the detected face left and right.
 * The tilt servo on D10 follows the detected face up and down.
 * When the Linux application reports that the face is lost,
 * the pan-tilt returns to the center.
 */

#include <Arduino_RouterBridge.h>
#include <Arduino_HardwareServo.h>

const int PAN_SERVO_PIN = 9;
const int TILT_SERVO_PIN = 10;

// Absolute servo angles — the center is 90°.
const int PAN_MIN_ANGLE = 45;
const int PAN_MAX_ANGLE = 135;
const int TILT_MIN_ANGLE = 45;
const int TILT_MAX_ANGLE = 115;
const int CENTER_ANGLE = 90;

const int STEP_DEGREES = 1;

HardwareServo panServo;
HardwareServo tiltServo;

int panAngle = CENTER_ANGLE;
int tiltAngle = CENTER_ANGLE;

int panStep(int direction)
{
    // direction > 0: face is right of center, turn right.
    panAngle += (direction > 0 ? STEP_DEGREES : -STEP_DEGREES);
    panAngle = constrain(panAngle, PAN_MIN_ANGLE, PAN_MAX_ANGLE);

    panServo.write(panAngle);
    return panAngle;
}

int tiltStep(int direction)
{
    // direction > 0: face is below center, tilt the camera down.
    tiltAngle += (direction > 0 ? STEP_DEGREES : -STEP_DEGREES);
    tiltAngle = constrain(tiltAngle, TILT_MIN_ANGLE, TILT_MAX_ANGLE);

    tiltServo.write(tiltAngle);
    return tiltAngle;
}

int centerPanTilt(String dummy)
{
    (void)dummy;

    panAngle = CENTER_ANGLE;
    tiltAngle = CENTER_ANGLE;

    panServo.write(CENTER_ANGLE);
    tiltServo.write(CENTER_ANGLE);
    return CENTER_ANGLE;
}

void setup()
{
    Serial.begin(115200);

    panServo.attach(PAN_SERVO_PIN);
    tiltServo.attach(TILT_SERVO_PIN);

    panServo.write(CENTER_ANGLE);
    tiltServo.write(CENTER_ANGLE);
    delay(500);

    Bridge.begin();

    Bridge.provide("pan_step", panStep);
    Bridge.provide("tilt_step", tiltStep);
    Bridge.provide("center_pan_tilt", centerPanTilt);

    Serial.println("=== Face Tracking Camera ===");
}

void loop()
{
    delay(20);
}
