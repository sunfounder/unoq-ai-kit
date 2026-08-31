/*
 * IMU Servo — tilt the board to move the pan-tilt servos.
 *
 * Pan servo  -> pin 9
 * Tilt servo -> pin 10
 * IMU        -> I2C (Wire1)
 */

#include <Arduino_HardwareServo.h>
#include "SunFounder_IMU.hpp"
#include "calibration_data.h"
#include "Wire.h"
#include <math.h>

SunFounder_IMU imu(&Wire1);
HardwareServo panServo;   // Pan servo on pin 9
HardwareServo tiltServo;  // Tilt servo on pin 10

const int minAngle = -45, maxAngle = 45;
const float deadZone = 5.0;
const int updateThreshold = 2, maxStep = 2;
const int sampleCount = 10;

int currentPanAngle = 0, currentTiltAngle = 0;
bool imuReady = false;

void setup() {
    Serial.begin(115200);

    panServo.attach(9);
    tiltServo.attach(10);
    panServo.write(90);   // Center both servos
    tiltServo.write(90);

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
}

void loop() {
    if (!imuReady) { delay(1000); return; }

    // Average 10 samples to reduce noise
    float accelX = 0, accelY = 0, accelZ = 0;
    for (int i = 0; i < sampleCount; i++) {
        imu.read();
        Vector3f accel = imu.get_accel();
        accelX += accel.x; accelY += accel.y; accelZ += accel.z;
        delay(2);
    }
    accelX /= sampleCount; accelY /= sampleCount; accelZ /= sampleCount;

    // Convert to angles
    float roll  = atan2(accelY, accelZ) * 180.0 / PI;
    float pitch = atan2(-accelX, sqrt(accelY*accelY + accelZ*accelZ))
                  * 180.0 / PI;

    // Dead zone
    if (fabs(roll)  < deadZone) roll  = 0;
    if (fabs(pitch) < deadZone) pitch = 0;

    int targetPan  = constrain((int)roll, minAngle, maxAngle);
    int targetTilt = constrain((int)-pitch, minAngle, maxAngle);

    // Smooth incremental steps
    if (abs(targetPan - currentPanAngle) >= updateThreshold) {
        if (targetPan > currentPanAngle)
            currentPanAngle += min(maxStep, targetPan - currentPanAngle);
        else
            currentPanAngle -= min(maxStep, currentPanAngle - targetPan);
        panServo.write(90 + currentPanAngle);
    }
    if (abs(targetTilt - currentTiltAngle) >= updateThreshold) {
        if (targetTilt > currentTiltAngle)
            currentTiltAngle += min(maxStep, targetTilt - currentTiltAngle);
        else
            currentTiltAngle -= min(maxStep, currentTiltAngle - targetTilt);
        tiltServo.write(90 + currentTiltAngle);
    }

    delay(20);
}
