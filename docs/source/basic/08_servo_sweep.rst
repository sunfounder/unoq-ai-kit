.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

08 Servo Sweep
===========

In the last lesson, you controlled a DC motor — it spins continuously, great for fans and wheels. Now you'll meet the **servo motor**: a motor that doesn't just spin, but moves to a precise angle and holds it. Servos are how robots point cameras, steer cars, and move joints. In this lesson, you'll make a servo sweep back and forth in a smooth, controlled motion.

In this lesson, you will learn to:

* Control a servo motor with the RobotShield ``Servo`` class
* Set the servo to a **precise angle** with ``setAngle()``
* Create smooth sweeping motion with ``for`` loops
* Understand the difference between **continuous rotation** (DC motor) and **positional control** (servo)

1. Build the Circuit
----------------------

**Components Needed**

.. list-table::
   :widths: 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * USB Cable
   * - |list_pan_tilt|
     - |list_usb_cable|


**Wiring Diagram**

The Pan Tilt Kit is already assembled. Connect the servo to channel 0 on the Robot Shield's servo header.

.. image:: /img/wiring/wiring_servo.png
   :width: 500
   :align: center

.. warning::

   Never force the servo horn by hand while it's powered — the internal gears can strip.

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


#. Navigate to the ``unoq-ai-kit/basic/`` folder and select ``08 Servo Sweep.zip``. The app appears in **My Apps** — click it to open.

#. With the app open, click the **Run** button (▶) in the top-right corner.

   .. note::      
   
      This project uses the **RobotShield** library. see :ref:`install_update_lib_c` for installation or updating.
   
   .. image:: /img/app_run.png
      :width: 500


#. Wait a few seconds for the upload to finish. The servo should start sweeping smoothly from -45° to +45° and back — like a radar scanning or a windshield wiper. Open the Serial Monitor to see the current angle in real time.

**The Sketch (sketch.ino)**

Now that you've seen the servo sweep, let's look at the sketch file that controls it.

.. code-block:: cpp
   :linenos:

   /*
    * Sweeps a servo on channel 0 between -45° and +45°.
    */

   #include "RobotShield.h"

   Servo servo(0);  // Servo on channel 0

   void setup() {
       Serial.begin(115200);
       I2cBus::i2c().begin();
       servo.begin();

       Serial.println("=== ServoSweep Ready ===");
   }

   void loop() {
       // Sweep from -45° to +45°
       for (int16_t angle = -45; angle <= 45; angle += 2) {
           servo.setAngle(angle);
           Serial.print("Servo 0 angle: ");
           Serial.println(angle);
           delay(30);
       }

       // Sweep back from +45° to -45°
       for (int16_t angle = 45; angle >= -45; angle -= 2) {
           servo.setAngle(angle);
           Serial.print("Servo 0 angle: ");
           Serial.println(angle);
           delay(30);
       }
   }

**How it Works**

The servo is your first **positional actuator** — instead of setting a speed, you set a target angle and the servo moves there automatically. The code uses ``for`` loops to create smooth sweeping motion:

.. code-block:: text

   setup() → runs once at startup:
       Start Serial Monitor
       Initialize I2C bus (Robot Shield communication)
       Initialize servo on channel 0

   loop() → runs over and over forever:
       Sweep right: for angle = -45 to +45 (step +2 each time):
           Set servo to that angle
           Print angle to Serial Monitor
           Wait 30ms
       Sweep left: for angle = +45 to -45 (step -2 each time):
           Set servo to that angle
           Print angle to Serial Monitor
           Wait 30ms
       (repeat — sweeps continuously)

#. Library Include and Servo Object Declaration

   - ``Servo servo(0)`` creates a ``Servo`` object on **channel 0** — the first 3-pin servo header on the Robot Shield
   - If you plug your servo into a different channel, simply change the number to match

   .. code-block:: arduino

      #include "RobotShield.h"
      Servo servo(0);

#. Setup: Initializing the Servo

   - ``servo.begin()`` must be called in ``setup()`` after starting the I2C bus
   - This prepares the Robot Shield to send position commands to the servo
   - The same initialization pattern used with the ``Pwm`` and ``Motor`` classes

   .. code-block:: arduino

      void setup() {
          Serial.begin(115200);
          I2cBus::i2c().begin();
          servo.begin();
      }

#. Sweeping Right with a For Loop

   - The ``for`` loop starts the servo at -45° and increases by 2° every 30 ms until it reaches +45°
   - ``int16_t`` is a 16-bit signed integer that can hold negative values
   - With each step, ``servo.setAngle(angle)`` commands the servo to that exact position — the internal feedback loop handles the rest

   .. code-block:: arduino

      for (int16_t angle = -45; angle <= 45; angle += 2) {
          servo.setAngle(angle);
          delay(30);
      }

#. Sweeping Left Back to Start

   - The second loop reverses direction, stepping from +45° back down to -45°
   - The same 2° step and 30 ms delay produce a smooth, continuous back-and-forth sweep
   - The sweep repeats indefinitely as ``loop()`` runs over and over

   .. code-block:: arduino

      for (int16_t angle = 45; angle >= -45; angle -= 2) {
          servo.setAngle(angle);
          delay(30);
      }

**Servo vs. DC Motor — What's the Difference?**

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Feature
     - DC Motor (used earlier)
     - Servo (This Lesson)
   * - Movement
     - Continuous rotation
     - Moves to a specific angle and stops
   * - Control
     - Speed and direction (``setPower``)
     - Angle (``setAngle``)
   * - Feedback
     - None — spins at whatever speed power allows
     - Built-in potentiometer — knows its exact position
   * - Holding
     - Doesn't hold position when stopped
     - Actively holds position against external force
   * - Typical use
     - Fans, wheels, drills
     - Steering, camera gimbals, robotic arms

A servo is essentially a DC motor with a gearbox, a potentiometer (for position feedback), and a tiny controller board — all in one package. When you call ``setAngle(30)``, the servo's internal controller reads the potentiometer, compares it to 30°, and drives the motor until they match.

3. Experiment
----------------

**Change the Sweep Range and Speed**

Try adjusting the sweep parameters and observe the effect:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Change
     - Effect
   * - ``angle += 5``, ``delay(10)``
     - Faster sweep — larger steps, shorter pauses
   * - ``angle += 1``, ``delay(50)``
     - Very smooth, slow sweep — nearly continuous motion
   * - Range ``0`` to ``90``
     - Only sweeps on the positive side (half the arc)
   * - Range ``-90`` to ``90``
     - Full 180° sweep — the servo's maximum range

Try pushing the servo arm gently while it's holding a position (use very light force). You'll feel it resist — the servo is actively fighting to maintain its commanded angle. This is the feedback loop at work.

**Challenge: Bounce Between Two Angles**

Instead of a smooth sweep, make the servo snap quickly between two positions — like a metronome or a turn signal. Go from -30° to +30° with a short pause at each end.

.. dropdown:: Click to reveal solution
   :open:

   .. code-block:: cpp

      void loop() {
          servo.setAngle(-30);   // Snap left
          delay(500);
          servo.setAngle(30);    // Snap right
          delay(500);
      }

   The servo moves at its maximum speed between positions — no gradual steps. Try different angle pairs: (-60, 60) for a wider swing, or (-10, 10) for a subtle wiggle. Adjust the ``delay()`` to control the dwell time at each position.

**Challenge: Knob-Controlled Servo**

Connect a potentiometer (used in the Analog Input lesson) to A2 and use it to control the servo angle in real time — turn the knob, the servo follows. This is how RC car steering and volume knobs on audio equipment work.

.. dropdown:: Click to reveal solution
   :open:

   .. code-block:: cpp

      #include "RobotShield.h"

      Servo servo(0);
      const int potPin = A2;

      void setup() {
          Serial.begin(115200);
          I2cBus::i2c().begin();
          servo.begin();

          Serial.println("=== Knob-Controlled Servo ===");
      }

      void loop() {
          int potValue = analogRead(potPin);
          int angle = map(potValue, 0, 1023, -90, 90);  // Map knob to servo range

          servo.setAngle(angle);

          Serial.print("Potentiometer: ");
          Serial.print(potValue);
          Serial.print("  Angle: ");
          Serial.println(angle);

          delay(20);  // Fast response — 50 updates per second
      }

   Turn the knob fully left → servo moves to -90°. Turn fully right → servo moves to +90°. Every position in between maps smoothly. The short ``delay(20)`` gives near-instant response. This is a complete **analog input → position output** system — the same control pattern used in robotic arms, pan-tilt camera mounts, and model aircraft.

4. Troubleshooting
--------------------

**Servo does not move at all**

* **Cause:** The servo cable is plugged in backwards, the battery isn't connected, or the wrong channel is selected in code.
* **Solution:** Check the servo connector orientation: Brown = GND, Red = 5V, Orange = Signal. Make sure it's plugged into channel 0 (the port matching ``Servo servo(0)`` in the code). Verify the battery pack is connected and has fresh batteries.

**Servo jitters or vibrates in place**

* **Cause:** The servo is trying to hold a position but the angle updates too frequently, or the power supply is unstable.
* **Solution:** Increase the ``delay()`` between angle updates to 50ms or more. Check that the battery pack is charged.

**Servo moves to the wrong angle or overshoots**

* **Cause:** The angle range exceeds the servo's physical limits, or the ``map()`` output range is wrong.
* **Solution:** The SG90 servo's safe range is approximately -90° to +90°. Sending angles beyond this range may cause the servo to hit its internal mechanical stop, producing a buzzing sound. Reduce the range to -80° to +80° to be safe.

**Servo moves erratically or randomly**

* **Cause:** The battery is low or there's a loose connection.
* **Solution:** Replace with fresh batteries and check all wiring.


* **Cause:** The board is not connected, or App Lab can't find it.
* **Solution:** Check the USB-C cable is firmly connected at both ends. Try unplugging and re-plugging it. In App Lab, make sure your UNO Q is detected.

5. Summary
-------------

Your robot just gained a joint! Servos bring precision and control to motion — instead of "spinning," you say "go to 45 degrees and stay there." In this lesson, you learned:

* How a servo motor differs from a DC motor — positional control vs. continuous rotation
* How to command a precise angle with ``servo.setAngle()``
* How to create smooth sweeping motion with ``for`` loops and small angle steps
* How a servo holds its position using an internal potentiometer feedback loop
* How to map an analog input (potentiometer) directly to servo angle — the foundation of remote control

In the next lesson, you'll return to the potentiometer — but this time using it to shift the pitch of a melody played through a passive buzzer.
