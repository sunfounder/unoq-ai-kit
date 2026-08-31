/*
 * IoT Control Center
 *
 * FINAL WIRING
 *
 * DHT11 DATA       -> D5
 * PIR OUT          -> D4
 * Ultrasonic TRIG  -> D3
 * Ultrasonic ECHO  -> D2
 * Joystick X       -> A3
 * Joystick Y       -> A2
 * 10-Axis IMU      -> I2C / Wire1
 *
 * Motor            -> M0
 * Pan servo        -> P0
 * Tilt servo       -> P1
 * Camera           -> CSI (handled by Python)
 */

#include <Arduino_RouterBridge.h>
#include "RobotShield.h"
#include "DHT.h"
#include "SunFounder_IMU.hpp"
#include "calibration_data.h"
#include "Wire.h"


// ---------------- Pins ----------------

const int DHT_PIN = 5;
const int PIR_PIN = 4;

const int TRIG_PIN = 3;
const int ECHO_PIN = 2;

const int JOYSTICK_X_PIN = A3;
const int JOYSTICK_Y_PIN = A2;

#define DHT_TYPE DHT11


// ---------------- Devices ----------------

DHT dht(DHT_PIN, DHT_TYPE);

SunFounder_IMU imu(&Wire1);

Motor motor("M0", 4, 5);

Servo panServo(0);
Servo tiltServo(1);


// ---------------- Control State ----------------

bool systemRunning = true;
bool motorEnabled = false;

const int MOTOR_POWER = 30;

int panAngle = 0;
int tiltAngle = 0;

int xCenter = 512;
int yCenter = 512;

const int MIN_ANGLE = -45;
const int MAX_ANGLE = 45;
const int DEAD_ZONE = 100;
const int STEP_SIZE = 1;


// ---------------- Timers ----------------

unsigned long lastEnvironmentUpdate = 0;
unsigned long lastJoystickUpdate = 0;
unsigned long lastImuUpdate = 0;

const unsigned long ENV_INTERVAL = 2000;
const unsigned long JOYSTICK_INTERVAL = 60;
const unsigned long IMU_INTERVAL = 500;


// ---------------- Ultrasonic ----------------

float getDistance()
{
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);

    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);

    digitalWrite(TRIG_PIN, LOW);

    unsigned long duration =
        pulseIn(ECHO_PIN, HIGH, 30000);

    if (duration == 0)
    {
        return -1.0;
    }

    return duration * 0.0343 / 2.0;
}


// ---------------- Joystick ----------------

void calibrateJoystick()
{
    long xTotal = 0;
    long yTotal = 0;

    // Do not touch the joystick during startup calibration.
    for (int i = 0; i < 20; i++)
    {
        xTotal += analogRead(JOYSTICK_X_PIN);
        yTotal += analogRead(JOYSTICK_Y_PIN);
        delay(10);
    }

    xCenter = xTotal / 20;
    yCenter = yTotal / 20;
}


void updateJoystick()
{
    int xValue =
        analogRead(JOYSTICK_X_PIN);

    int yValue =
        analogRead(JOYSTICK_Y_PIN);

    // Same mapping as the tested Joystick Servo example:
    // Y -> Pan P0
    // X -> Tilt P1

    if (systemRunning)
    {
        if (yValue > yCenter + DEAD_ZONE)
        {
            panAngle += STEP_SIZE;
        }
        else if (yValue < yCenter - DEAD_ZONE)
        {
            panAngle -= STEP_SIZE;
        }

        if (xValue > xCenter + DEAD_ZONE)
        {
            tiltAngle += STEP_SIZE;
        }
        else if (xValue < xCenter - DEAD_ZONE)
        {
            tiltAngle -= STEP_SIZE;
        }

        panAngle =
            constrain(
                panAngle,
                MIN_ANGLE,
                MAX_ANGLE
            );

        tiltAngle =
            constrain(
                tiltAngle,
                MIN_ANGLE,
                MAX_ANGLE
            );

        panServo.setAngle(panAngle);
        tiltServo.setAngle(tiltAngle);
    }

    Bridge.notify(
        "joystick_update",
        xValue,
        yValue,
        panAngle,
        tiltAngle
    );
}


// ---------------- Environment ----------------

void sendEnvironmentData()
{
    float humidity =
        dht.readHumidity();

    float temperature =
        dht.readTemperature();

    if (isnan(humidity) ||
        isnan(temperature))
    {
        Serial.println(
            "Failed to read from DHT11!"
        );

        return;
    }

    bool pirDetected =
        digitalRead(PIR_PIN) == HIGH;

    float distance =
        getDistance();

    Bridge.notify(
        "environment_update",
        temperature,
        humidity,
        pirDetected,
        distance
    );

    Serial.print("Temp: ");
    Serial.print(temperature, 1);

    Serial.print(" C  Humidity: ");
    Serial.print(humidity, 1);

    Serial.print("%  PIR: ");
    Serial.print(
        pirDetected ? "Motion" : "Clear"
    );

    Serial.print("  Distance: ");

    if (distance < 0)
    {
        Serial.println("Out of range");
    }
    else
    {
        Serial.print(distance, 1);
        Serial.println(" cm");
    }
}


// ---------------- 10-Axis IMU ----------------

void sendImuData()
{
    imu.read();

    Vector3f accel = {0, 0, 0};
    Vector3f gyro = {0, 0, 0};
    Vector3f mag = {0, 0, 0};

    float azimuth = 0;
    float pressure = 0;
    float altitude = 0;
    float imuTemperature = 0;

    if (imu.is_motion_sensor_found())
    {
        accel = imu.get_accel();
        gyro = imu.get_gyro();
    }

    if (imu.is_magnetometer_found())
    {
        mag = imu.get_magnetometer();
        azimuth = imu.get_azimuth();
    }

    if (imu.is_barometer_found())
    {
        pressure = imu.get_pressure();
        altitude = imu.get_altitude();
        imuTemperature =
            imu.get_temperature();
    }

    Bridge.notify(
        "imu_update",
        accel.x,
        accel.y,
        accel.z,
        gyro.x,
        gyro.y,
        gyro.z,
        mag.x,
        mag.y,
        mag.z,
        azimuth,
        pressure,
        altitude,
        imuTemperature
    );
}


// ---------------- Web UI Controls ----------------

void updateMotor()
{
    if (systemRunning &&
        motorEnabled)
    {
        motor.setPower(
            MOTOR_POWER
        );
    }
    else
    {
        motor.setPower(0);
    }
}


void setMotorEnabled(bool enabled)
{
    motorEnabled = enabled;

    updateMotor();

    Serial.print("Motor M0: ");

    if (systemRunning &&
        motorEnabled)
    {
        Serial.println("30%");
    }
    else
    {
        Serial.println("OFF");
    }
}


void setSystemRunning(bool enabled)
{
    systemRunning = enabled;

    if (!systemRunning)
    {
        motor.setPower(0);

        panAngle = 0;
        tiltAngle = 0;

        panServo.setAngle(0);
        tiltServo.setAngle(0);

        Serial.println(
            "System Run: OFF"
        );
    }
    else
    {
        updateMotor();

        panServo.setAngle(
            panAngle
        );

        tiltServo.setAngle(
            tiltAngle
        );

        Serial.println(
            "System Run: ON"
        );
    }
}


// ---------------- Setup ----------------

void setup()
{
    Serial.begin(115200);

    pinMode(PIR_PIN, INPUT);

    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);

    digitalWrite(TRIG_PIN, LOW);

    dht.begin();

    // Robot Shield motor + servos
    I2cBus::i2c().begin();

    motor.begin();
    motor.setPower(0);

    panServo.begin();
    tiltServo.begin();

    panServo.setAngle(0);
    tiltServo.setAngle(0);

    // 10-Axis IMU
    Wire1.begin();
    imu.begin();

    imu.set_accel_bias(
        ACCEL_BIAS
    );

    imu.set_accel_scale(
        ACCEL_SCALE
    );

    imu.set_gyro_bias(
        GYRO_BIAS
    );

    imu.set_gyro_scale(
        GYRO_SCALE
    );

    imu.set_magnetometer_bias(
        MAG_BIAS
    );

    imu.set_magnetometer_scale(
        MAG_SCALE
    );

    // Bridge
    Bridge.begin();

    Bridge.provide(
        "set_motor_enabled",
        setMotorEnabled
    );

    Bridge.provide(
        "set_system_running",
        setSystemRunning
    );

    delay(500);

    calibrateJoystick();

    Serial.println(
        "=== IoT Control Center ==="
    );

    Serial.println(
        "DHT11: D5"
    );

    Serial.println(
        "PIR: D4"
    );

    Serial.println(
        "Ultrasonic: TRIG D3 / ECHO D2"
    );

    Serial.println(
        "Joystick: X A3 / Y A2"
    );

    Serial.println(
        "Motor: M0"
    );

    Serial.println(
        "Servos: P0 / P1"
    );

    Serial.print(
        "Joystick X center: "
    );

    Serial.println(xCenter);

    Serial.print(
        "Joystick Y center: "
    );

    Serial.println(yCenter);
}


// ---------------- Main Loop ----------------

void loop()
{
    unsigned long now =
        millis();

    if (
        now - lastJoystickUpdate >=
        JOYSTICK_INTERVAL
    )
    {
        lastJoystickUpdate = now;
        updateJoystick();
    }

    if (
        now - lastEnvironmentUpdate >=
        ENV_INTERVAL
    )
    {
        lastEnvironmentUpdate = now;
        sendEnvironmentData();
    }

    if (
        now - lastImuUpdate >=
        IMU_INTERVAL
    )
    {
        lastImuUpdate = now;
        sendImuData();
    }

    delay(5);
}
