/*
 * Gesture Control
 *
 * The Linux application recognizes hand gestures and calls the
 * Bridge functions below:
 *   - set_rgb_color:  light the RGB LED (D6/D7/D8)
 *   - center_pan_tilt: return the pan-tilt to the center (D9/D10)
 */

#include <Arduino_RouterBridge.h>
#include <Arduino_HardwareServo.h>

const int RGB_R_PIN = 6;
const int RGB_G_PIN = 7;
const int RGB_B_PIN = 8;

const int PAN_SERVO_PIN = 9;
const int TILT_SERVO_PIN = 10;

const int CENTER_ANGLE = 90;

HardwareServo panServo;
HardwareServo tiltServo;

int rgbR = 0;
int rgbG = 0;
int rgbB = 0;

void applyRgb()
{
    analogWrite(RGB_R_PIN, rgbR);
    analogWrite(RGB_G_PIN, rgbG);
    analogWrite(RGB_B_PIN, rgbB);
}

int setRgbColor(int r, int g, int b)
{
    rgbR = constrain(r, 0, 255);
    rgbG = constrain(g, 0, 255);
    rgbB = constrain(b, 0, 255);
    applyRgb();
    return 0;
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
    Serial.begin(115200);

    pinMode(RGB_R_PIN, OUTPUT);
    pinMode(RGB_G_PIN, OUTPUT);
    pinMode(RGB_B_PIN, OUTPUT);
    setRgbColor(0, 0, 0);

    panServo.attach(PAN_SERVO_PIN);
    tiltServo.attach(TILT_SERVO_PIN);
    panServo.write(CENTER_ANGLE);
    tiltServo.write(CENTER_ANGLE);
    delay(500);

    Bridge.begin();

    Bridge.provide("set_rgb_color", setRgbColor);
    Bridge.provide("center_pan_tilt", centerPanTilt);

    Serial.println("=== Gesture Control ===");
}

void loop()
{
    delay(20);
}
