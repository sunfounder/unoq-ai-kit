/*
 * Motion-Controlled Servo (IMU Servo)
 *
 * Tilt the IMU left/right to control the pan servo on channel 0.
 * Tilt forward/back to control the tilt servo on channel 1.
 * When the IMU is level, both servos return to center (0°).
 *
 * Uses accelerometer data to calculate roll and pitch angles,
 * with multi-sample averaging, a dead zone, and smooth stepping
 * to eliminate jitter.
 */

#include "RobotShield.h"
#include "SunFounder_IMU.hpp"
#include "calibration_data.h"
#include "Wire.h"
#include <math.h>

SunFounder_IMU imu(&Wire1);

Servo panServo(0);    // Pan servo on channel 0
Servo tiltServo(1);   // Tilt servo on channel 1

// ---- Configuration ----

const int minAngle = -45;
const int maxAngle = 45;

const float deadZone = 5.0;        // Ignore tilt below this (degrees)
const int updateThreshold = 2;     // Minimum angle change to move servo
const int maxStep = 2;             // Max degrees per update (smoothing)
const int sampleCount = 10;        // IMU samples to average per frame

int currentPanAngle = 0;
int currentTiltAngle = 0;
bool imuReady = false;

// ----

void setup() {
    Serial.begin(115200);

    // Initialize Robot Shield and servos
    I2cBus::i2c().begin();
    panServo.begin();
    tiltServo.begin();
    panServo.setAngle(0);
    tiltServo.setAngle(0);

    // Initialize IMU with calibration
    Wire1.begin();
    imuReady = imu.begin();

    if (imuReady) {
        imu.set_accel_bias(ACCEL_BIAS);
        imu.set_accel_scale(ACCEL_SCALE);
        imu.set_gyro_bias(GYRO_BIAS);
        imu.set_gyro_scale(GYRO_SCALE);
        imu.set_magnetometer_bias(MAG_BIAS);
        imu.set_magnetometer_scale(MAG_SCALE);
    }

    Serial.println("=== Motion-Controlled Servo ===");
    if (!imuReady) {
        Serial.println("WARNING: IMU not detected — servos will not move.");
    } else {
        Serial.println("IMU ready. Tilt the board to move the servos.");
    }
}

void loop() {
    if (!imuReady) {
        delay(1000);
        return;
    }

    // Read multiple samples and average to reduce noise
    float accelX = 0, accelY = 0, accelZ = 0;

    for (int i = 0; i < sampleCount; i++) {
        imu.read();
        Vector3f accel = imu.get_accel();
        accelX += accel.x;
        accelY += accel.y;
        accelZ += accel.z;
        delay(2);
    }

    accelX /= sampleCount;
    accelY /= sampleCount;
    accelZ /= sampleCount;

    // Convert accelerometer data to roll and pitch angles
    float roll  = atan2(accelY, accelZ) * 180.0 / PI;
    float pitch = atan2(-accelX, sqrt(accelY * accelY + accelZ * accelZ))
                  * 180.0 / PI;

    // Dead zone — ignore tiny tilts
    if (fabs(roll) < deadZone)  roll = 0;
    if (fabs(pitch) < deadZone) pitch = 0;

    // Map IMU angles to servo targets
    int targetPan  = constrain((int)roll, minAngle, maxAngle);
    int targetTilt = constrain((int)-pitch, minAngle, maxAngle);

    // Smoothly step pan servo toward target
    if (abs(targetPan - currentPanAngle) >= updateThreshold) {
        if (targetPan > currentPanAngle) {
            currentPanAngle += min(maxStep, targetPan - currentPanAngle);
        } else {
            currentPanAngle -= min(maxStep, currentPanAngle - targetPan);
        }
        panServo.setAngle(currentPanAngle);
    }

    // Smoothly step tilt servo toward target
    if (abs(targetTilt - currentTiltAngle) >= updateThreshold) {
        if (targetTilt > currentTiltAngle) {
            currentTiltAngle += min(maxStep, targetTilt - currentTiltAngle);
        } else {
            currentTiltAngle -= min(maxStep, currentTiltAngle - targetTilt);
        }
        tiltServo.setAngle(currentTiltAngle);
    }

    Serial.print("Roll: ");  Serial.print(roll, 1);
    Serial.print("  Pitch: "); Serial.print(pitch, 1);
    Serial.print("  Pan: ");   Serial.print(currentPanAngle);
    Serial.print("  Tilt: ");  Serial.println(currentTiltAngle);

    delay(20);
}
