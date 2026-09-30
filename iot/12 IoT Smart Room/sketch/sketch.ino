/*
 * 12 IoT Smart Room
 *
 * Motor IN1        -> D2 (PWM)
 * Motor IN2        -> D3 (PWM)
 * PIR OUT          -> D4
 * DHT11 DATA       -> D5
 * RGB LED R        -> D8
 * RGB LED G        -> D7
 * RGB LED B        -> D6
 * Pan servo        -> D9
 * Tilt servo       -> D10
 * Photoresistor    -> A0
 * Camera           -> CSI (Python)
 *
 * The pan-tilt is aimed from the Web UI or by voice commands, so no joystick
 * module is needed.
 */

#include <Arduino_RouterBridge.h>
#include <Arduino_HardwareServo.h>
#include "DHT.h"

const int MOTOR_IN1_PIN = 2;
const int MOTOR_IN2_PIN = 3;
const int PIR_PIN = 4;
const int DHT_PIN = 5;
const int RGB_R_PIN = 8;
const int RGB_G_PIN = 7;
const int RGB_B_PIN = 6;
const int PAN_SERVO_PIN = 9;
const int TILT_SERVO_PIN = 10;
const int LIGHT_SENSOR_PIN = A0;

#define DHT_TYPE DHT11

DHT dht(DHT_PIN, DHT_TYPE);
HardwareServo panServo;
HardwareServo tiltServo;

bool systemRunning = true;
bool fanEnabled = false;

const int FAN_POWER_PERCENT = 30;
const int FAN_PWM = 255 * FAN_POWER_PERCENT / 100;

int rgbR = 0;
int rgbG = 0;
int rgbB = 0;

const int LEFT_ANGLE = 135;
const int RIGHT_ANGLE = 45;
const int UP_ANGLE = 45;
const int DOWN_ANGLE = 115;
const int CENTER_ANGLE = 90;

/* How far one nudge from the Web UI moves the servos. */
const int STEP_DEGREES = 10;

int panAngle = CENTER_ANGLE;
int tiltAngle = CENTER_ANGLE;

unsigned long lastEnvironmentUpdate = 0;
const unsigned long ENV_INTERVAL = 1000;


void stopFan()
{
    analogWrite(MOTOR_IN1_PIN, 0);
    analogWrite(MOTOR_IN2_PIN, 0);
}


void runFan()
{
    analogWrite(MOTOR_IN1_PIN, FAN_PWM);
    analogWrite(MOTOR_IN2_PIN, 0);
}


void updateFan()
{
    if (systemRunning && fanEnabled)
        runFan();
    else
        stopFan();
}


void setFanEnabled(bool enabled)
{
    fanEnabled = enabled;
    updateFan();
}


void applyRgb()
{
    if (!systemRunning)
    {
        analogWrite(RGB_R_PIN, 0);
        analogWrite(RGB_G_PIN, 0);
        analogWrite(RGB_B_PIN, 0);
        return;
    }

    analogWrite(RGB_R_PIN, rgbR);
    analogWrite(RGB_G_PIN, rgbG);
    analogWrite(RGB_B_PIN, rgbB);
}


void setRgbColor(int r, int g, int b)
{
    rgbR = constrain(r, 0, 255);
    rgbG = constrain(g, 0, 255);
    rgbB = constrain(b, 0, 255);
    applyRgb();
}


void setSystemRunning(bool enabled)
{
    systemRunning = enabled;
    updateFan();
    applyRgb();

    if (!systemRunning)
    {
        panAngle = CENTER_ANGLE;
        tiltAngle = CENTER_ANGLE;
        panServo.write(CENTER_ANGLE);
        tiltServo.write(CENTER_ANGLE);
    }
}


/* ---- absolute moves, used by the voice commands ---- */

int panLeft(String dummy)
{
    (void)dummy;
    panAngle = LEFT_ANGLE;
    panServo.write(panAngle);
    return panAngle;
}


int panRight(String dummy)
{
    (void)dummy;
    panAngle = RIGHT_ANGLE;
    panServo.write(panAngle);
    return panAngle;
}


int tiltUp(String dummy)
{
    (void)dummy;
    tiltAngle = UP_ANGLE;
    tiltServo.write(tiltAngle);
    return tiltAngle;
}


int tiltDown(String dummy)
{
    (void)dummy;
    tiltAngle = DOWN_ANGLE;
    tiltServo.write(tiltAngle);
    return tiltAngle;
}


int centerPanTilt(String dummy)
{
    (void)dummy;
    panAngle = CENTER_ANGLE;
    tiltAngle = CENTER_ANGLE;
    panServo.write(panAngle);
    tiltServo.write(tiltAngle);
    return CENTER_ANGLE;
}


/* ---- relative moves, used by the Web UI arrow keys ---- */

int panStep(int delta)
{
    panAngle = constrain(panAngle + delta, RIGHT_ANGLE, LEFT_ANGLE);
    panServo.write(panAngle);
    return panAngle;
}


int tiltStep(int delta)
{
    tiltAngle = constrain(tiltAngle + delta, UP_ANGLE, DOWN_ANGLE);
    tiltServo.write(tiltAngle);
    return tiltAngle;
}


void sendEnvironmentData()
{
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();

    if (isnan(humidity) || isnan(temperature))
        return;

    bool motion = digitalRead(PIR_PIN) == HIGH;
    int lightRaw = analogRead(LIGHT_SENSOR_PIN);

    Bridge.notify(
        "environment_update",
        temperature,
        humidity,
        motion,
        lightRaw
    );
}


void setup()
{
    Serial.begin(115200);

    pinMode(PIR_PIN, INPUT);

    pinMode(MOTOR_IN1_PIN, OUTPUT);
    pinMode(MOTOR_IN2_PIN, OUTPUT);
    stopFan();

    pinMode(RGB_R_PIN, OUTPUT);
    pinMode(RGB_G_PIN, OUTPUT);
    pinMode(RGB_B_PIN, OUTPUT);
    setRgbColor(0, 0, 0);

    dht.begin();

    panServo.attach(PAN_SERVO_PIN);
    tiltServo.attach(TILT_SERVO_PIN);
    panServo.write(CENTER_ANGLE);
    tiltServo.write(CENTER_ANGLE);
    delay(500);

    Bridge.begin();

    Bridge.provide("set_fan_enabled", setFanEnabled);
    Bridge.provide("set_rgb_color", setRgbColor);
    Bridge.provide("set_system_running", setSystemRunning);
    Bridge.provide("pan_left", panLeft);
    Bridge.provide("pan_right", panRight);
    Bridge.provide("tilt_up", tiltUp);
    Bridge.provide("tilt_down", tiltDown);
    Bridge.provide("center", centerPanTilt);
    Bridge.provide("pan_step", panStep);
    Bridge.provide("tilt_step", tiltStep);

    Serial.println("=== IoT Smart Room ===");
    Serial.println("Pan servo: D9, Tilt servo: D10");
    Serial.println("Photoresistor: A0");
    Serial.println("RGB LED: D8 / D7 / D6");
}


void loop()
{
    unsigned long now = millis();

    if (now - lastEnvironmentUpdate >= ENV_INTERVAL)
    {
        lastEnvironmentUpdate = now;
        sendEnvironmentData();
    }

    delay(5);
}
