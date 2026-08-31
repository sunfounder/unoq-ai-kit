#pragma once

/*
 * IMU Calibration Data
 *
 * Run calibrate.ino first to generate calibration values for your specific
 * sensor, then copy the results here. Using calibrated values significantly
 * improves accuracy by compensating for factory offsets in each sensor.
 *
 * Default values (all zeros for bias, 1.0 for scale) correspond to
 * uncalibrated mode — the sensor will work but readings may drift.
 */

// ---- Accelerometer ----
const float ACCEL_BIAS[3]  = {0.0, 0.0, 0.0};
const float ACCEL_SCALE[3] = {1.0, 1.0, 1.0};

// ---- Gyroscope ----
const float GYRO_BIAS[3]  = {0.0, 0.0, 0.0};
const float GYRO_SCALE[3] = {1.0, 1.0, 1.0};

// ---- Magnetometer ----
const float MAG_BIAS[3]  = {0.0, 0.0, 0.0};
const float MAG_SCALE[3] = {1.0, 1.0, 1.0};

// ---- Barometer (optional) ----
// Uncomment and adjust these to fine-tune barometer readings:
// const float BARO_PRESSURE_OFFSET    = 0.0f;      // hPa
// const float BARO_SEALEVEL_PRESSURE = 1013.25f;   // hPa
// const float GRAVITY                = 9.80665f;    // m/s^2
