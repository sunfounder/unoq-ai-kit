/*
 * Reads 10-axis IMU sensor data via I2C on the AVIO Carrier.
 * Outputs accelerometer, gyroscope, magnetometer, and barometer readings
 * to the Serial Monitor every second.
 *
 * Uses the SunFounder_IMU library and calibration data from calibration_data.h.
 * To calibrate your IMU, run calibrate.ino first and copy the results into
 * calibration_data.h before running this sketch.
 */

#include "SunFounder_IMU.hpp"
#include "calibration_data.h"

#include "Wire.h"

SunFounder_IMU imu(&Wire1);

void setup() {
    Serial.begin(115200);
    while (!Serial) {
        delay(100);
    }

    Wire1.begin();
    imu.begin();

    // Apply calibration data
    imu.set_accel_bias(ACCEL_BIAS);
    imu.set_accel_scale(ACCEL_SCALE);
    imu.set_gyro_bias(GYRO_BIAS);
    imu.set_gyro_scale(GYRO_SCALE);
    imu.set_magnetometer_bias(MAG_BIAS);
    imu.set_magnetometer_scale(MAG_SCALE);

    // Optional: uncomment to override barometer/gravity defaults
    // imu.set_gravity(GRAVITY);
    // imu.set_barometer_pressure_offset(BARO_PRESSURE_OFFSET);
    // imu.set_barometer_sealevel_pressure(BARO_SEALEVEL_PRESSURE);

    Serial.println("=== IMU Attitude Sensor ===");
    Serial.println("Reading accelerometer, gyroscope, magnetometer & barometer...");
}

void loop() {
    imu.read();

    // ---- Accelerometer & Gyroscope ----
    if (imu.is_motion_sensor_found()) {
        Vector3f accel = imu.get_accel();
        Vector3f gyro = imu.get_gyro();

        Serial.print("Accel (m/s^2): ");
        Serial.print(accel.x);
        Serial.print(", ");
        Serial.print(accel.y);
        Serial.print(", ");
        Serial.println(accel.z);

        Serial.print("Gyro (deg/s): ");
        Serial.print(gyro.x);
        Serial.print(", ");
        Serial.print(gyro.y);
        Serial.print(", ");
        Serial.println(gyro.z);
    }

    // ---- Magnetometer ----
    if (imu.is_magnetometer_found()) {
        Vector3f mag = imu.get_magnetometer();
        float azimuth = imu.get_azimuth();

        Serial.print("Mag (Gauss): ");
        Serial.print(mag.x);
        Serial.print(", ");
        Serial.print(mag.y);
        Serial.print(", ");
        Serial.println(mag.z);

        Serial.print("Azimuth: ");
        Serial.print(azimuth);
        Serial.println(" degrees");
    }

    // ---- Barometer ----
    if (imu.is_barometer_found()) {
        float temperature = imu.get_temperature();
        float pressure = imu.get_pressure();
        float altitude = imu.get_altitude();

        Serial.print("Temperature: ");
        Serial.print(temperature);
        Serial.println(" °C");

        Serial.print("Pressure: ");
        Serial.print(pressure);
        Serial.println(" hPa");

        Serial.print("Altitude: ");
        Serial.print(altitude);
        Serial.println(" m");
    }

    Serial.println("---");
    delay(1000);
}
