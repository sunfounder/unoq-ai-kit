#pragma once

// Accel gyro and magnetometer calibration data,
// calibrate with calibrate.ino and copy the result here:


const float ACCEL_BIAS[3] = {0.02, 0.01, -0.01};
const float ACCEL_SCALE[3] = {1.00, 0.99, 1.00};
const float GYRO_BIAS[3] = {1.89, 1.00, -0.22};
const float GYRO_SCALE[3] = {4.15, 1.17, 8.47};
const float MAG_BIAS[3] = {-0.00, -0.18, -0.35};
const float MAG_SCALE[3] = {1.06, 0.90, 1.08};

// Barometer pressure offset in hPa
// const float BARO_PRESSURE_OFFSET = 0.0f;
// Sealevel pressure in hPa
// const float BARO_SEALEVEL_PRESSURE = 1013.25f;
// Gravity in m/s^2
// const float GRAVITY = 9.80665f;
