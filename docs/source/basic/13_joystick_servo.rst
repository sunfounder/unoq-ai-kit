.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

13 Joystick Servo
======================

You've controlled LEDs with buttons, pitch with potentiometers, and motors with thermistors. Now you'll combine a joystick — essentially two potentiometers at right angles — with two servos to create a **pan-tilt controller**. Push the stick left/right to pan, up/down to tilt, and press it down to reset both to center. This is the same mechanism behind security cameras, drone gimbals, and robotic arms.

In this lesson, you will learn to:

* Read a joystick — two analog axes plus a digital button in one module
* Control two servos simultaneously with incremental positioning
* Implement **auto-calibration** to find the joystick's true center
* Use a **dead zone** to prevent drift when the stick is at rest

1. Build the Circuit
----------------------

**Components Needed**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_joystick`
     - 1 * :ref:`cpn_breadboard`
     - Several :ref:`cpn_wires`
   * - |list_pan_tilt|
     - |list_joystick_module|
     - |list_breadboard|
     - |list_wire|
   * - 1 * USB Cable
     -
     -
     -
   * - |list_usb_cable|
     -
     -
     -

.. tip::

   The Pan Tilt Kit includes the UNO Q, Robot Shield, two servos, camera, battery, and structural parts — already assembled. The joystick module has five pins: VCC and GND power it, VRx and VRy output X and Y positions, and SW is a push button. Connect **VCC to 3.3V** (not 5V) — the UNO Q's analog inputs measure 0–3.3V, and VRx/VRy feed A3/A2.

**Wiring Diagram**

Follow the diagram below to place each component on the breadboard and connect the wires.

.. image:: /img/wiring/wiring_joystick_servo.png
   :width: 600
   :align: center

2. Code
----------

**Import and Run the Code**

All code for this course is provided as ``.zip`` files that you can import directly into App Lab.

#. Open **Arduino App Lab**, go to **My Apps**. Click the dropdown arrow next to **Create new app +** and select **Import App**.

   .. image:: /img/app_import_app.png
      :width: 600


#. Select **Import from Computer**.

   .. image:: /img/app_import_pc.png
      :width: 600


#. Navigate to the ``unoq-ai-kit/basic/`` folder and select ``13 Joystick Servo.zip``. The app appears in **My Apps** — click it to open.

#. With the app open, click the **Run** button (▶) in the top-right corner.

   .. note::      
      
      This project uses the **RobotShield** library. see :ref:`install_update_lib_c` for installation or updating.
   
   .. image:: /img/app_run.png
      :width: 500


#. Wait a few seconds for the upload to finish. **Do not touch the joystick for the first second** — the sketch auto-calibrates its center position. Then move the stick — the pan servo follows left/right, the tilt servo follows up/down. Press the stick to reset both to 0°.

**The Sketch (sketch.ino)**

Now that you've seen the joystick control both servos, let's look at the sketch file.

.. code-block:: cpp
   :linenos:

   #include "RobotShield.h"

   const int swPin = 2, xPin = A3, yPin = A2;
   Servo panServo(0), tiltServo(1);

   int panAngle = 0, tiltAngle = 0;
   int xCenter = 512, yCenter = 512;
   const int minAngle = -45, maxAngle = 45;
   const int deadZone = 100, stepSize = 1;

   void setup() {
       Serial.begin(115200);
       pinMode(swPin, INPUT_PULLUP);
       I2cBus::i2c().begin();
       panServo.begin();   panServo.setAngle(0);
       tiltServo.begin();  tiltServo.setAngle(0);
       delay(500);

       // Auto-calibrate center position
       long xTotal = 0, yTotal = 0;
       for (int i = 0; i < 20; i++) {
           xTotal += analogRead(xPin);
           yTotal += analogRead(yPin);
           delay(10);
       }
       xCenter = xTotal / 20;
       yCenter = yTotal / 20;

       Serial.println("=== Joystick Servo Control Ready ===");
   }

   void loop() {
       // Button press → reset to center
       if (digitalRead(swPin) == LOW) {
           panAngle = 0; tiltAngle = 0;
           panServo.setAngle(0); tiltServo.setAngle(0);
           delay(300); return;
       }

       int xValue = analogRead(xPin);
       int yValue = analogRead(yPin);

       // Incremental control with dead zone
       if (yValue > yCenter + deadZone)       panAngle += stepSize;
       else if (yValue < yCenter - deadZone)  panAngle -= stepSize;
       if (xValue > xCenter + deadZone)       tiltAngle += stepSize;
       else if (xValue < xCenter - deadZone)  tiltAngle -= stepSize;

       panAngle  = constrain(panAngle, minAngle, maxAngle);
       tiltAngle = constrain(tiltAngle, minAngle, maxAngle);

       panServo.setAngle(panAngle);
       tiltServo.setAngle(tiltAngle);

       Serial.print("X: "); Serial.print(xValue);
       Serial.print("  Y: "); Serial.print(yValue);
       Serial.print("  Pan: "); Serial.print(panAngle);
       Serial.print("  Tilt: "); Serial.println(tiltAngle);

       delay(30);
   }

**How it Works**

This lesson combines all three types of I/O — analog input (joystick axes), digital input (button), and servo output — into a single interactive system:

.. code-block:: text

   setup() → runs once at startup:
       Initialize servos at 0° (center)
       Auto-calibrate: read X and Y 20 times, average to find center
       Print ready message with calibration values

   loop() → runs over and over forever:
       Button pressed? → reset both servos to 0°, skip rest
       Read X and Y axis values
       Outside dead zone?
           Y > center + 100 → pan right (step +1°)
           Y < center - 100 → pan left  (step -1°)
           X > center + 100 → tilt right (step +1°)
           X < center - 100 → tilt left  (step -1°)
       Constrain angles to ±45°
       Update both servos
       Wait 30ms, repeat

1. **Pin Declarations, Servo Objects, and Variables**

   - The joystick provides three inputs: X position on A3, Y position on A2, and a button on pin 2
   - Two ``Servo`` objects are created on channels 0 and 1 for pan and tilt
   - ``deadZone`` and ``stepSize`` constants control sensitivity and movement granularity

   .. code-block:: arduino

      const int swPin = 2, xPin = A3, yPin = A2;
      Servo panServo(0), tiltServo(1);

      int panAngle = 0, tiltAngle = 0;
      int xCenter = 512, yCenter = 512;
      const int minAngle = -45, maxAngle = 45;
      const int deadZone = 100, stepSize = 1;

2. **Auto-Calibration in Setup**

   - Every joystick has a slightly different center voltage due to manufacturing tolerances
   - This loop reads both axes 20 times, sums the values, and averages them to find the true center
   - The code adapts to your specific joystick without any hardcoded values

   .. code-block:: arduino

      long xTotal = 0, yTotal = 0;
      for (int i = 0; i < 20; i++) {
          xTotal += analogRead(xPin);
          yTotal += analogRead(yPin);
          delay(10);
      }
      xCenter = xTotal / 20;
      yCenter = yTotal / 20;

3. **Incremental Control with a Dead Zone**

   - If the joystick is pushed beyond the dead zone (100 units from center), the angle changes by one degree per loop iteration
   - The dead zone prevents servo twitching from tiny voltage fluctuations when the stick is at rest
   - The incremental approach gives smooth, deliberate motion instead of instant jumps

   .. code-block:: arduino

      if (yValue > yCenter + deadZone)       panAngle += stepSize;
      else if (yValue < yCenter - deadZone)  panAngle -= stepSize;
      if (xValue > xCenter + deadZone)       tiltAngle += stepSize;
      else if (xValue < xCenter - deadZone)  tiltAngle -= stepSize;

4. **Constraining Angles and Updating Servos**

   - ``constrain()`` clamps both angles to the ±45° range, preventing the servos from exceeding mechanical limits
   - Even if the stick is held at the extreme edge, the servos stay within their safe range
   - The two ``setAngle()`` calls command both servos to their current positions

   .. code-block:: arduino

      panAngle  = constrain(panAngle, minAngle, maxAngle);
      tiltAngle = constrain(tiltAngle, minAngle, maxAngle);

      panServo.setAngle(panAngle);
      tiltServo.setAngle(tiltAngle);

5. **Why Incremental Instead of Direct Mapping?**

   - Direct mapping (``panAngle = map(yValue, 0, 1023, -45, 45)``) works for LEDs but not for servos
   - A joystick returns to center when released, so direct mapping would snap the servo back immediately
   - Incremental control holds the last position when the stick centers, giving precise, deliberate positioning like a real pan-tilt controller

3. Experiment
----------------

**Adjust the Dead Zone**

The dead zone determines how far you must push the stick before the servos move. Try different values and observe the feel:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - ``deadZone`` Value
     - Effect
   * - 50
     - Very sensitive — slight touch moves the servo
   * - 100
     - Balanced — default, comfortable for most users
   * - 200
     - Stiff — requires deliberate push, good for coarse positioning
   * - 0
     - No dead zone — servo may jitter due to electrical noise

**Challenge: Adjust the Movement Speed**

Change ``stepSize`` from 1 to 3 and observe how the servos move faster but less smoothly. Try stepSize = 5 for very fast motion. What's the trade-off between speed and smoothness?

Larger stepSize = faster movement but choppier motion. 

* At stepSize = 1, the servo moves like a precision instrument. 
* At stepSize = 5, it feels like a video game controller. 
* The ideal value depends on your application — surgical robots use tiny steps, game controllers use larger ones.

4. Troubleshooting
--------------------

**Servos don't move at all**

* **Cause:** The battery is not connected, or the RobotShield I2C bus isn't initialized.
* **Solution:** Connect the battery pack to the Robot Shield. Verify ``I2cBus::i2c().begin()`` is called before ``servo.begin()``. Also check that ``servo.setAngle()`` is being called — uncomment the Serial prints to verify.

**Servos jitter or twitch at rest**

* **Cause:** The dead zone is too small, or the auto-calibration ran while the stick was being moved.
* **Solution:** Increase ``deadZone`` to 150. Restart and don't touch the joystick during the first second of startup — this is when auto-calibration runs. If the center was calibrated incorrectly, the dead zone won't work properly.

**One axis moves in the wrong direction**

* **Cause:** The joystick's VRx and VRy pins are swapped.
* **Solution:** Check that VRx connects to A3 and VRy to A2. If they're reversed, the X axis controls tilt and Y controls pan — swap the wires to fix.

**Servo hits the mechanical limit and buzzes**

* **Cause:** The ``constrain()`` range is too wide for your servo.
* **Solution:** Some servos have a narrower range than ±45°. Reduce ``maxAngle`` and ``minAngle`` to ±30° and test. If the buzzing stops, your servo's physical range is smaller.

**Joystick button doesn't reset servos**

* **Cause:** The button pin isn't using INPUT_PULLUP, or the switch pin is miswired.
* **Solution:** Verify the SW pin of the joystick connects to D2, and the code uses ``pinMode(swPin, INPUT_PULLUP)``. Without INPUT_PULLUP, the pin floats and gives random readings.

5. Summary
-------------

You've built a two-axis pan-tilt controller — the same mechanism behind countless real-world devices. In this lesson, you learned:

* How a joystick combines two potentiometers and a button into one intuitive input device
* How auto-calibration makes code adapt to hardware variations — no hardcoded values
* How a dead zone filters out noise when the stick is at rest
* How incremental control gives smooth, precise servo positioning
* How to control two servos independently and constrain their range for safety

In the next lesson, you'll replace the joystick with an IMU — tilting the board itself to control the servos, like the motion controls in a smartphone or game controller.
