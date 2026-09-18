# 14 IMU Attitude

Read data from the 10-axis IMU (Inertial Measurement Unit) on the Multimedia Carrier via I2C. Outputs accelerometer (motion), gyroscope (rotation), magnetometer (compass heading), and barometer (temperature, pressure, altitude) readings to the Serial Monitor every second. Uses the SunFounder_IMU library with calibration support for improved accuracy.



## Libraries Used

- **SunFounder_IMU** library


## Hardware

- Pan Tilt Kit ×1
- 10-Axis IMU x1
- 4pin Cable x1
- USB-C cable ×1


## Wiring

The IMU is connected to the UNO Q QWIIC connector — no breadboard wiring needed, just attach the carrier to the UNO Q.

![Wiring Diagram](assets/docs_assets/wiring_imu.png)

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Download [14 IMU Attitude.zip](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/14.IMU.Attitude.zip) and import it in **Arduino App Lab**.
4. Click **Run**.
5. Open the **Serial Monitor**. You'll see accelerometer (m/s²), gyroscope (deg/s), magnetometer (Gauss), azimuth (degrees), temperature (°C), pressure (hPa), and altitude (m) readings every second. Pick up the board and tilt it — watch the values change in real time.

> **Calibration:** for best accuracy, run the **14 IMU Calibration** project first, then copy the calibration output into `calibration_data.h` (in this project's `sketch/` folder) and re-run this sketch with the updated values.

## How it Works

**Flow**

- `setup()` — waits for the Serial Monitor, initializes the I2C bus and IMU with `imu.begin()`, then applies the calibration data
- `loop()` — calls `imu.read()` once, prints whichever sensors are found, and waits 1 second

**Ten sensors on two wires**

Every sensor on the I2C bus has its own address — the library calls the address, the right chip answers, and everyone else stays quiet. That's why a 10-axis IMU only needs a couple of wires (`Wire1.begin()`).

**Applying calibration**

`imu.set_accel_bias()`, `imu.set_gyro_bias()`, and the matching scale setters correct the raw readings: bias subtracts a constant offset (fixing a gyro that reads 2 deg/s while perfectly still) and scale multiplies by a factor to fix sensitivity errors — the values come from the calibration project you run first.

**One call reads everything**

A single `imu.read()` fills the library's internal state with every connected sensor; getters like `imu.get_accel()` then pull out individual values, already converted to real units (m/s², deg/s, Gauss, hPa).

**Checking each sensor before printing**

Each sensor group is guarded by an `is_*_found()` check, so the sketch skips gracefully if part of the IMU isn't detected — the rest of the readings still print.

