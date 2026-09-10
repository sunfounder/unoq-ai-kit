/*
 * Certification Test
 *
 * Exposes every peripheral to Python through Bridge:
 *
 *   Motor IN1        -> D2
 *   Motor IN2        -> D3
 *   Ultrasonic TRIG  -> D4
 *   Ultrasonic ECHO  -> D5
 *   PIR OUT          -> D6
 *   Joystick SW      -> D7
 *   Joystick X       -> A3
 *   Joystick Y       -> A2
 *   DHT11 DATA       -> D8
 *   Pan servo        -> D9
 *   Tilt servo       -> D10
 *   IMU              -> QWIIC (Wire1, I2C)
 */

#include <Arduino_RouterBridge.h>
#include <Arduino_HardwareServo.h>
#include "DHT.h"
#include "SunFounder_IMU.hpp"
#include "Wire.h"

const int MOTOR_IN1_PIN = 2;
const int MOTOR_IN2_PIN = 3;
const int TRIG_PIN = 4;
const int ECHO_PIN = 5;
const int PIR_PIN = 6;
const int JOY_SW_PIN = 7;
const int JOY_X_PIN = A3;
const int JOY_Y_PIN = A2;
const int DHT_PIN = 8;
const int PAN_SERVO_PIN = 9;
const int TILT_SERVO_PIN = 10;

#define DHT_TYPE DHT11

DHT dht(DHT_PIN, DHT_TYPE);
SunFounder_IMU imu(&Wire1);
HardwareServo panServo;
HardwareServo tiltServo;

// ── Motor ────────────────────────────────────────────────

int setMotor(int speed)
{
    speed = constrain(speed, -255, 255);

    if (speed > 0) {
        analogWrite(MOTOR_IN1_PIN, speed);   // forward
        analogWrite(MOTOR_IN2_PIN, 0);
    } else if (speed < 0) {
        analogWrite(MOTOR_IN1_PIN, 0);
        analogWrite(MOTOR_IN2_PIN, -speed);  // reverse
    } else {
        analogWrite(MOTOR_IN1_PIN, 0);
        analogWrite(MOTOR_IN2_PIN, 0);       // stop
    }

    return speed;
}

// ── Ultrasonic ───────────────────────────────────────────

float readDistance(String dummy)
{
    (void)dummy;

    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long duration = pulseIn(ECHO_PIN, HIGH, 30000);
    return duration * 0.0343 / 2.0;
}

// ── PIR ──────────────────────────────────────────────────

int readPir(String dummy)
{
    (void)dummy;
    return digitalRead(PIR_PIN) == HIGH ? 1 : 0;
}

// ── Joystick ─────────────────────────────────────────────

String readJoystick(String dummy)
{
    (void)dummy;

    String result = String(analogRead(JOY_X_PIN));
    result += ",";
    result += String(analogRead(JOY_Y_PIN));
    result += ",";
    result += digitalRead(JOY_SW_PIN) == LOW ? "1" : "0";
    return result;
}

// ── DHT11 ────────────────────────────────────────────────

String readDht(String dummy)
{
    (void)dummy;

    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();

    if (isnan(humidity) || isnan(temperature)) {
        return "error";
    }

    String result = String(temperature, 1);
    result += ",";
    result += String(humidity, 1);
    return result;
}

// ── Servos ───────────────────────────────────────────────

int setPan(int angle)
{
    panServo.write(constrain(angle, 0, 180));
    return angle;
}

int setTilt(int angle)
{
    tiltServo.write(constrain(angle, 0, 180));
    return angle;
}

// ── IMU ──────────────────────────────────────────────────

String readImu(String dummy)
{
    (void)dummy;

    if (!imu.begin()) {
        return "error";
    }

    imu.read();

    if (!imu.is_motion_sensor_found()) {
        return "error";
    }

    Vector3f accel = imu.get_accel();
    Vector3f gyro = imu.get_gyro();

    String result = String(accel.x, 2);
    result += ",";
    result += String(accel.y, 2);
    result += ",";
    result += String(accel.z, 2);
    result += ",";
    result += String(gyro.x, 2);
    result += ",";
    result += String(gyro.y, 2);
    result += ",";
    result += String(gyro.z, 2);
    return result;
}

void setup()
{
    Serial.begin(115200);

    pinMode(MOTOR_IN1_PIN, OUTPUT);
    pinMode(MOTOR_IN2_PIN, OUTPUT);
    setMotor(0);

    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    pinMode(PIR_PIN, INPUT);
    pinMode(JOY_SW_PIN, INPUT_PULLUP);

    dht.begin();

    panServo.attach(PAN_SERVO_PIN);
    tiltServo.attach(TILT_SERVO_PIN);
    panServo.write(90);
    tiltServo.write(90);
    delay(500);

    Wire1.begin();

    Bridge.begin();

    Bridge.provide("set_motor", setMotor);
    Bridge.provide("read_distance", readDistance);
    Bridge.provide("read_pir", readPir);
    Bridge.provide("read_joystick", readJoystick);
    Bridge.provide("read_dht", readDht);
    Bridge.provide("set_pan", setPan);
    Bridge.provide("set_tilt", setTilt);
    Bridge.provide("read_imu", readImu);

    Serial.println("=== Certification Test ===");
}

void loop()
{
    delay(20);
}
