.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

15 IMU Servo
======================

Earlier, you used a joystick to control servos — you pushed a stick and the servo followed. Now you'll remove the joystick entirely. **Tilt the board itself** and the servos respond — just like tilting a smartphone to steer a racing game, or the motion controls in a VR headset. The IMU provides the motion data; the servos do the moving; and the math you'll learn converts gravity into angles.

In this lesson, you will learn to:

* Convert accelerometer data into **roll and pitch** angles using ``atan2()``
* Apply **multi-sample averaging** to smooth noisy sensor data
* Use incremental servo control with a **dead zone** for fluid, jitter-free motion
* Fuse two concepts learned earlier — IMU readings and servo control — into one integrated system

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

  * ``Arduino_HardwareServo`` (drives the servo with hardware PWM)
  * ``SunFounder_IMU`` (reads the 10-axis IMU sensor data)

**Wiring Diagram**

Connect the IMU to the UNO Q's QWIIC connector (no wiring needed), then plug the pan servo into pin 9 and the tilt servo into pin 10 on the Robot Shield's servo headers.


.. image:: /img/wiring/wiring_imu_servo.png
   :width: 600
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

#. Open ``15 IMU Servo.zip`` in App Lab and navigate to ``sketch/calibration_data.h``.

#. Replace the calibration values in ``calibration_data.h`` with the ones you copied from the calibration step.

   .. image:: img/11_replace_value.png


#. Click the **Run** button (▶) in the top-right corner.

   .. note::      
    
        This project uses the **Arduino_HardwareServo** and **SunFounder_IMU** libraries. see :ref:`install_update_lib_c` for installation or updating.
   
   .. image:: /img/app_run.png
      :width: 500


#. Wait a few seconds for the upload to finish. Keep the board still for the first second, then hold it level — both servos should be centered at their neutral position (90° on the Arduino_HardwareServo API). Tilt the board left/right to pan, forward/back to tilt. The servos follow your motion smoothly.

**The Sketch (sketch.ino)**

Now that you've seen the IMU drive the servos, let's look at the sketch file.

.. code-block:: cpp
   :linenos:

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

**How it Works**

This lesson fuses IMU sensor data with servo control — the same principle behind camera gimbals, drone stabilizers, and smartphone screen rotation:

.. code-block:: text

   setup() → runs once at startup:
       Attach pan servo to pin 9, tilt servo to pin 10
       Center both servos with write(90)
       Initialize IMU with calibration data

   loop() → runs over and over forever:
       Read 10 accelerometer samples, average them
       atan2(accelY, accelZ) → roll angle (tilt left/right)
       atan2(-accelX, ...)   → pitch angle (tilt forward/back)
       Apply dead zone (ignore < 5°)
       Constrain target to ±45°
       Step servos smoothly toward target (max 2° per frame)
       Write 90° + offset to each servo
       Wait 20ms, repeat (~50 Hz update rate)

1. **Library Includes and Hardware Objects**

   - The includes bring in the standard **Arduino_HardwareServo** library, the IMU library, the calibration data header, I2C, and math functions
   - The UNO Q uses ``Arduino_HardwareServo`` because it drives the servo with the STM32's hardware PWM — the standard Servo library causes jitter on this board
   - The IMU is created on the ``Wire1`` I2C bus; the two ``HardwareServo`` objects are attached to pins 9 and 10 and centered with ``write(90)``

   .. code-block:: arduino

      #include <Arduino_HardwareServo.h>
      #include "SunFounder_IMU.hpp"
      #include "calibration_data.h"
      #include "Wire.h"
      #include <math.h>

      SunFounder_IMU imu(&Wire1);
      HardwareServo panServo;   // Pan servo on pin 9
      HardwareServo tiltServo;  // Tilt servo on pin 10

      panServo.attach(9);
      tiltServo.attach(10);
      panServo.write(90);   // Center both servos
      tiltServo.write(90);

2. **Multi-Sample Averaging to Reduce Noise**

   - The accelerometer is read 10 times per frame, summed, and divided by the count to produce an average
   - Without averaging, electrical noise would cause the servos to twitch randomly
   - Averaging smooths out short-term fluctuations while preserving the real motion signal

   .. code-block:: arduino

      float accelX = 0, accelY = 0, accelZ = 0;
      for (int i = 0; i < sampleCount; i++) {
          imu.read();
          Vector3f accel = imu.get_accel();
          accelX += accel.x; accelY += accel.y; accelZ += accel.z;
          delay(2);
      }
      accelX /= sampleCount;
      accelY /= sampleCount;
      accelZ /= sampleCount;

3. **Converting Accelerometer Readings to Angles**

   - ``atan2(y, x)`` is the arctangent function that converts the ratio of two accelerometer axes into an angle
   - ``atan2(accelY, accelZ)`` calculates roll (left/right tilt), and ``atan2(-accelX, sqrt(Y² + Z²))`` calculates pitch (forward/back tilt)
   - Both results are in radians, so multiplying by 180/π converts them to degrees

   .. code-block:: arduino

      float roll  = atan2(accelY, accelZ) * 180.0 / PI;
      float pitch = atan2(-accelX, sqrt(accelY*accelY + accelZ*accelZ))
                    * 180.0 / PI;

4. **Dead Zone and Incremental Stepping**

   - The dead zone ignores tilt angles smaller than 5°, creating a stable region where tiny vibrations and noise do not affect the servos
   - ``constrain()`` clamps the target angles to the safe ±45° range
   - Incremental stepping changes the servo angle by at most 2° per update, preventing jerky motion that would stress the servo gears
   - ``write(90 + angle)`` converts the ±45° offset into the Arduino_HardwareServo library's 0–180° range, where 90° is the centered position

   .. code-block:: arduino

      if (fabs(roll)  < deadZone) roll  = 0;
      if (fabs(pitch) < deadZone) pitch = 0;

      int targetPan  = constrain((int)roll, minAngle, maxAngle);
      int targetTilt = constrain((int)-pitch, minAngle, maxAngle);

      if (abs(targetPan - currentPanAngle) >= updateThreshold) {
          if (targetPan > currentPanAngle)
              currentPanAngle += min(maxStep, targetPan - currentPanAngle);
          else
              currentPanAngle -= min(maxStep, currentPanAngle - targetPan);
          panServo.write(90 + currentPanAngle);
      }

**The Math: From Gravity to Angles**

When the board is perfectly level, gravity points straight down — 100% on the Z axis (≈9.8 m/s²). When you tilt the board, gravity "spills" onto the X and Y axes. The ratio tells you the angle:

  **Roll = atan2(Y_accel, Z_accel)** — If you tilt left, Y increases and Z decreases, so atan2(Y/Z) gives the angle.

  **Pitch = atan2(-X_accel, √(Y² + Z²))** — If you tilt forward, X becomes negative. The total gravity in the Y-Z plane is √(Y² + Z²), so atan2(-X / √(Y²+Z²)) gives the forward angle.

This is the same math your smartphone uses to rotate the screen when you turn it sideways.

3. Experiment
----------------

**Change the Dead Zone**

The dead zone determines how steady you must hold the board before the servos respond:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - ``deadZone`` Value
     - Effect
   * - 2.0
     - Very sensitive — the slightest tilt moves the servo
   * - 5.0
     - Balanced — default, small vibrations filtered out
   * - 10.0
     - Requires deliberate tilt — good for shaky hands

**Challenge: Change the Smoothing**

Try changing ``maxStep`` from 2 to 5. The servos will move faster but less smoothly. Then try ``maxStep = 1`` for ultra-smooth motion. What feels best to you?


4. Troubleshooting
--------------------

**"IMU not detected" — servos don't move**

* **Cause:** The IMU initialization failed.
* **Solution:** Check the Serial Monitor for the startup message. If it prints "WARNING: IMU not detected", detach and reattach the Multimedia Carrier, then restart. Also verify ``Wire1.begin()`` is called before ``imu.begin()``.

**Servos jitter or shake continuously**

* **Cause:** The dead zone is too small, or ``sampleCount`` is too low.
* **Solution:** Increase ``deadZone`` to 8.0. Increase ``sampleCount`` to 20 — more samples = smoother but slightly slower response.

**Servos move in the wrong direction**

* **Cause:** The servos are swapped, or the angle sign needs to be reversed.
* **Solution:** Check that the pan servo is attached to pin 9 and tilt to pin 10. If they're swapped, the board's left tilt will move the "wrong" servo. You can swap the pin numbers in the ``attach()`` calls (``panServo.attach(9)`` / ``tiltServo.attach(10)``) or physically swap the servo connectors.

**Servo reaches limit and stops while board is still tilting**

* **Cause:** The tilt angle exceeds ±45° (the ``constrain()`` limit).
* **Solution:** This is normal — the servo is at its maximum safe angle. To increase the range, change ``minAngle`` and ``maxAngle``, but check that your servo can physically move that far first.

**Motion feels laggy or delayed**

* **Cause:** The ``delay(20)`` at the end of loop is too long, or ``maxStep`` is too small.
* **Solution:** Reduce the ``delay(20)`` to 10ms for faster updates. Increase ``maxStep`` to 3 or 4 for quicker servo response. Balance speed against smoothness.

5. Summary
-------------

You've built a motion-controlled pan-tilt system — the same technology inside camera gimbals, drone stabilizers, and VR controllers. In this lesson, you learned:

* How to convert raw accelerometer data into roll and pitch angles using ``atan2()``
* How multi-sample averaging reduces sensor noise for smooth control
* How a dead zone and incremental stepping create fluid, professional-grade motion
* How to fuse two previous lessons — IMU readings and servo control — into a single integrated system

You've come a long way from blinking a single LED. You can now read complex sensors over I2C, drive motors and servos, and process data with math that turns raw voltages into meaningful physical quantities. The skills you've learned are the foundation of robotics, drones, and countless other real-world systems.
