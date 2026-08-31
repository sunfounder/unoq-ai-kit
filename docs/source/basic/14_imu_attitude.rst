.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

14 IMU Attitude
==================

In previous lessons, your sensors communicated through simple voltages. The DHT11 took it a step further with a custom single-wire protocol. Now you'll use **I2C** — a two-wire bus that lets multiple sensors share the same pins. Your IMU packs four sensors into one chip, all talking through I2C: accelerometer (motion), gyroscope (rotation), magnetometer (compass), and barometer (altitude). You'll read all of them at once.

In this lesson, you will learn to:

* Understand I2C — a shared communication bus used by most complex sensors
* Read accelerometer, gyroscope, magnetometer, and barometer data
* Use calibration data to improve sensor accuracy
* Monitor multi-sensor data in the Serial Monitor

1. Setup
----------------------

**What You Need**

.. list-table::
   :widths: 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * USB Cable
     - 1 * 10-Axis IMU
   * - |list_pan_tilt|
     - |list_usb_cable|
     - |list_imu|

**Software Requirements**

This project uses the following sketch libraries:

* Libraries:

  * ``SunFounder_IMU`` (reads the 10-axis IMU sensor data)

**Wiring Diagram**

Plug the 10-Axis IMU into the UNO Q's QWIIC connector — no breadboard wiring is needed; it shares the I2C bus with the Robot Shield, and I2C lets multiple devices share the bus without conflict.

.. image:: /img/wiring/wiring_imu.png
   :width: 500
   :align: center

2. Run the App
----------------

**Step 1: Calibrate the IMU**

Before reading sensor data, calibrate the IMU to ensure accurate measurements.

#. Open **Arduino App Lab** and import ``14 IMU Calibration.zip`` from the ``unoq-ai-kit/basic/`` folder.

   .. image:: /img/app_import_app.png
      :width: 600

#. Click **Run** (▶) and open the **Serial Monitor** (📊).

   .. note::

      This project uses the ``SunFounder_IMU`` library. See :ref:`install_update_lib_c` for instructions on installing or updating the library.

#. Switch to the **Serial Monitor** window, then press **Enter** or type any character and press **Enter**. 

   * The calibration process will begin and display instructions for the first orientation.
   * Follow the on-screen prompts to place the device in each of the six orientations (**Z up**, **Z down**, **X up**, **X down**, **Y up**, and **Y down**). 
   * Keep the device completely still during each measurement, then press **Enter** (or send any character) to continue to the next step.

   .. image:: img/11_cali_enter.png

#. After all six orientations have been measured, the Serial Monitor displays the calibration constants. Copy the output—it should look similar to the following:

   .. code-block:: cpp

      ...

      const float ACCEL_BIAS[3] = {0.0041, 0.0344, -0.0547};
      const float ACCEL_SCALE[3] = {1.0025, 0.9945, 1.0017};
      const float GYRO_BIAS[3] = {2.2020, 2.2171, -0.1697};
      const float GYRO_SCALE[3] = {1.0000, 1.0000, 1.0000};
      const float MAG_BIAS[3] = {-0.1017, 0.1555, -0.0746};
      const float MAG_SCALE[3] = {0.9657, 1.1538, 0.9109};

      ...

**Step 2: Apply Calibration and Run**

#. Open ``14 IMU Attitude`` in App Lab and navigate to ``sketch/calibration_data.h``.

#. Replace the default calibration values with the ones you copied from the calibration step.

   .. image:: img/11_replace_value.png

#. Click **Run** (▶). Open the **Serial Monitor** — you should see accelerometer, gyroscope, magnetometer, and barometer readings every second. Pick up the board and tilt it — the values change in real time, now with improved accuracy.

   .. code-block:: text

      Accel (m/s^2): -0.12, -0.25, 9.74
      Gyro (deg/s): 0.01, 0.03, -0.57
      Mag ((Gauss)): -1.23, -0.05, -0.72
      Azimuth: 357.44 degrees
      Temperature: 28.89 °C
      Pressure: 1006.33 hPa
      Altitude: 57.75 m


**The Sketch (sketch.ino)**

Now that you've seen the IMU output all four sensor streams, let's look at the sketch file.

.. code-block:: cpp
   :linenos:

   #include "SunFounder_IMU.hpp"
   #include "calibration_data.h"
   #include "Wire.h"

   SunFounder_IMU imu(&Wire1);

   void setup() {
       Serial.begin(115200);
       while (!Serial) { delay(100); }

       Wire1.begin();
       imu.begin();

       imu.set_accel_bias(ACCEL_BIAS);
       imu.set_accel_scale(ACCEL_SCALE);
       imu.set_gyro_bias(GYRO_BIAS);
       imu.set_gyro_scale(GYRO_SCALE);
       imu.set_magnetometer_bias(MAG_BIAS);
       imu.set_magnetometer_scale(MAG_SCALE);

       Serial.println("=== IMU Attitude Sensor ===");
   }

   void loop() {
       imu.read();

       if (imu.is_motion_sensor_found()) {
           Vector3f accel = imu.get_accel();
           Vector3f gyro = imu.get_gyro();

           Serial.print("Accel (m/s^2): ");
           Serial.print(accel.x); Serial.print(", ");
           Serial.print(accel.y); Serial.print(", ");
           Serial.println(accel.z);

           Serial.print("Gyro (deg/s): ");
           Serial.print(gyro.x); Serial.print(", ");
           Serial.print(gyro.y); Serial.print(", ");
           Serial.println(gyro.z);
       }

       if (imu.is_magnetometer_found()) {
           Vector3f mag = imu.get_magnetometer();
           float azimuth = imu.get_azimuth();

           Serial.print("Mag (Gauss): ");
           Serial.print(mag.x); Serial.print(", ");
           Serial.print(mag.y); Serial.print(", ");
           Serial.println(mag.z);

           Serial.print("Azimuth: "); Serial.print(azimuth);
           Serial.println(" degrees");
       }

       if (imu.is_barometer_found()) {
           float temperature = imu.get_temperature();
           float pressure = imu.get_pressure();
           float altitude = imu.get_altitude();

           Serial.print("Temperature: "); Serial.print(temperature);
           Serial.println(" *C");
           Serial.print("Pressure: "); Serial.print(pressure);
           Serial.println(" hPa");
           Serial.print("Altitude: "); Serial.print(altitude);
           Serial.println(" m");
       }

       Serial.println("---");
       delay(1000);
   }

**How it Works**

This lesson introduces I2C communication — and works with the most sensor-rich device you've used so far. The code follows the same setup/loop rhythm, but reads from four different sensor subsystems inside one chip:

.. code-block:: text

   setup() → runs once at startup:
       Start Serial Monitor and wait for connection
       Initialize I2C bus (Wire1)
       Initialize IMU and load calibration data

   loop() → runs over and over forever:
       imu.read() — query all sensors at once
       Motion sensor found? → print accel + gyro
       Magnetometer found?  → print mag field + compass azimuth
       Barometer found?     → print temperature + pressure + altitude
       Wait 1 second, repeat

1. **Library Includes and IMU Object Creation**

   - ``SunFounder_IMU.hpp`` provides the library that handles all four sensors in the IMU
   - ``Wire.h`` is the standard Arduino I2C library; ``Wire1`` is the I2C bus the Multimedia Carrier uses
   - The IMU object is created with a reference to ``Wire1`` so it can communicate over that bus

   .. code-block:: arduino

      #include "SunFounder_IMU.hpp"
      #include "calibration_data.h"
      #include "Wire.h"

      SunFounder_IMU imu(&Wire1);

2. **Setup: I2C Bus, IMU Initialization, and Calibration**

   - ``Wire1.begin()`` starts the I2C bus, and ``imu.begin()`` initializes the sensor
   - ``set_*_bias()`` corrects for factory offsets (like a sensor reading 0.05g when flat)
   - ``set_*_scale()`` corrects for sensitivity errors; without calibration the sensor still works but readings may drift

   .. code-block:: arduino

      void setup() {
          Wire1.begin();
          imu.begin();

          imu.set_accel_bias(ACCEL_BIAS);
          imu.set_accel_scale(ACCEL_SCALE);
          imu.set_gyro_bias(GYRO_BIAS);
          imu.set_gyro_scale(GYRO_SCALE);
          imu.set_magnetometer_bias(MAG_BIAS);
          imu.set_magnetometer_scale(MAG_SCALE);
      }

3. **Reading Motion Sensor Data in the Loop**

   - ``imu.read()`` queries all four sensor subsystems in a single I2C command
   - ``is_motion_sensor_found()`` checks if the accelerometer and gyroscope are responding, skipping gracefully if not
   - ``Vector3f`` holds three float values (x, y, z), keeping the axes of acceleration or rotation together

   .. code-block:: arduino

      imu.read();

      if (imu.is_motion_sensor_found()) {
          Vector3f accel = imu.get_accel();
          Vector3f gyro = imu.get_gyro();

4. **Reading Magnetometer and Barometer Data**

   - Each sensor subsystem has its own ``is_*_found()`` check to handle failures gracefully
   - ``imu.get_azimuth()`` calculates the compass heading (0–360 degrees) from magnetometer data
   - ``imu.get_altitude()`` derives altitude from barometric pressure using the standard atmosphere model

   .. code-block:: arduino

      if (imu.is_magnetometer_found()) {
          float azimuth = imu.get_azimuth();
      }

      if (imu.is_barometer_found()) {
          float temperature = imu.get_temperature();
          float pressure = imu.get_pressure();
          float altitude = imu.get_altitude();
      }

5. **I2C Addresses**

   - Every I2C device has a unique 7-bit address that the UNO Q uses to select which device it talks to
   - All other devices on the bus ignore messages not addressed to them
   - The IMU's four sensors may each have their own address or share one; the library handles this transparently

3. Experiment
----------------

**Tilt the Board and Observe**

Pick up the UNO Q and slowly tilt it in different directions. Watch the Serial Monitor:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Motion
     - Expected Reading
   * - Board flat on table (Z up)
     - Accel Z ≈ +9.8 m/s² (gravity), X and Y ≈ 0
   * - Tilt board left
     - Accel X becomes positive, Z decreases
   * - Rotate board quickly
     - Gyro values spike during rotation, return to 0 when still
   * - Point board north
     - Azimuth ≈ 0° (or 360°)

**Challenge: Find the Gravity Vector**

The accelerometer always measures gravity (9.8 m/s² downward). When the board is flat, gravity is entirely on the Z axis. When tilted, gravity splits across axes. Calculate the total acceleration magnitude and verify it equals ~9.8 m/s² regardless of orientation:

.. dropdown:: Click to reveal solution
   :open:

   Add this after reading the accelerometer:

   .. code-block:: cpp

      float magnitude = sqrt(accel.x*accel.x + accel.y*accel.y + accel.z*accel.z);
      Serial.print("Magnitude: ");
      Serial.print(magnitude);
      Serial.println(" m/s^2");

   The magnitude should stay close to 9.8 no matter how you tilt the board — because gravity is constant.

**Challenge: Simple Level Detector**

Modify the code to print "LEVEL" when the board is approximately flat (X and Y acceleration close to 0, Z close to 9.8), and "TILTED" otherwise.

.. dropdown:: Click to reveal solution
   :open:

   .. code-block:: cpp

      if (abs(accel.x) < 1.0 && abs(accel.y) < 1.0 && accel.z > 8.0) {
          Serial.println("→ LEVEL");
      } else {
          Serial.println("→ TILTED");
      }

4. Troubleshooting
--------------------

**"IMU not detected" or no sensor output**

* **Cause:** The I2C bus isn't initialized, or the carrier isn't properly attached.
* **Solution:** Make sure the Multimedia Carrier is firmly connected to the UNO Q. Verify ``Wire1.begin()`` is called before ``imu.begin()``. Check the Serial Monitor for the startup message — if it says "WARNING: IMU not detected", the sensor isn't responding on the I2C bus.

**Readings are all zeros**

* **Cause:** The ``imu.read()`` call is failing silently.
* **Solution:** Check that ``imu.begin()`` returned successfully. Add ``Serial.println(imu.begin() ? "OK" : "FAIL");`` to confirm initialization.

**Accelerometer values drift or are inaccurate**

* **Cause:** The sensor is uncalibrated.
* **Solution:** Run the **14 IMU Calibration** project to generate calibration values for your specific sensor. Copy the output into ``calibration_data.h``. Without calibration, the default values (bias=0, scale=1) should still produce reasonable results — just less precise.

**I2C bus hangs or freezes**

* **Cause:** Another I2C device is conflicting, or the bus is in a stuck state.
* **Solution:** Power-cycle the board (unplug USB, wait 5 seconds, reconnect). I2C buses rarely conflict on the UNO Q because the IMU and Robot Shield use different addresses.


* **Cause:** The board is not connected, or App Lab can't find it.
* **Solution:** Check the USB-C cable is firmly connected at both ends. Try unplugging and re-plugging it.

5. Summary
-------------

Congratulations! You've used I2C — the most common communication bus for complex sensors — and read data from four different sensor types at once. In this lesson, you learned:

* How I2C lets multiple sensors share the same two wires using unique addresses
* How to read accelerometer (motion), gyroscope (rotation), magnetometer (compass), and barometer (altitude) data
* How calibration bias and scale improve sensor accuracy
* How the SunFounder_IMU library abstracts away complex I2C register reads

In the next lesson, you'll put your calibrated IMU to work in real time — converting accelerometer data into roll and pitch angles to control two servos with the tilt of your hand, like a camera gimbal or a drone stabilizer.
