.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

07 Motor Speed Controller
=========================

LEDs, buzzers, and sensors are all about light, sound, and data — but what about **motion**? In this lesson, you'll control your first actuator that physically moves: a **DC motor**. Spin it forward to blow air with a fan blade, reverse it to change direction, and vary the speed from a gentle breeze to full blast. Motors are the muscles of robotics — and you're about to make something move.

In this lesson, you will learn to:

* Control a DC motor with a direction pin and a PWM pin
* Set motor **speed** with ``analogWrite()`` values (0–255)
* Control motor **direction** with a HIGH/LOW digital pin
* Understand why motors need a **separate power source** (battery) — USB alone isn't enough

1. Setup
----------------------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_motor_xh254`
     - 1 * Fan Blade
     - 1 * USB Cable
   * - |list_pan_tilt|
     - |list_motor|
     - |list_fan|
     - |list_usb_cable|

**Software Requirements**

This project uses no external libraries — the sketch only uses the built-in Arduino framework.

**Wiring Diagram**

The motor connects to the Robot Shield's **M0** terminal — its direction pin goes to **D4** and its PWM speed pin to **D5**.

.. image:: /img/wiring/wiring_motor.png
   :width: 600
   :align: center

2. Run the App
----------------

**Import and Run the Code**

All code for this course is provided as ``.zip`` files that you can import directly into App Lab.

#. Open **Arduino App Lab**, go to **Apps**. Click the dropdown arrow next to **Create new app +** and select **Import App**.

   .. image:: /img/app_import_app.png
      :width: 600


#. Select **Import from Computer**.

   .. image:: /img/app_import_pc.png
      :width: 600


#. Navigate to the ``unoq-ai-kit/basic/`` folder and select ``07 Motor Speed Controller.zip``. The app appears in **Apps** — click it to open.

#. With the app open, click the **Run** button (▶) in the top-right corner.

   .. image:: /img/app_run.png
      :width: 500


#. Wait a few seconds for the upload to finish. The motor should spin **forward for 3 seconds**, brake for 1 second, spin **backward for 3 seconds**, then brake for 3 seconds — repeating this cycle indefinitely. If you attached the fan blade, you'll feel the airflow change direction.

**The Sketch (sketch.ino)**

Now that you've seen the motor in action, let's look at the sketch file.

.. code-block:: cpp
   :linenos:

   /*
    * Drives a DC motor on the Robot Shield's M0 terminal:
    * forward → stop → reverse → stop.
    *
    * M0 direction pin -> D4
    * M0 PWM pin       -> D5
    */

   const int motorDirPin = 4;  // Motor direction control
   const int motorPwmPin = 5;  // Motor speed control (PWM)

   void setup() {
       Serial.begin(115200);

       pinMode(motorDirPin, OUTPUT);
       pinMode(motorPwmPin, OUTPUT);
       analogWrite(motorPwmPin, 0);  // Motor starts stopped

       Serial.println("=== MotorTest Ready ===");
   }

   void loop() {
       Serial.println("M0: Forward 50%");
       digitalWrite(motorDirPin, HIGH);   // Forward direction
       analogWrite(motorPwmPin, 128);     // ~50% speed (0-255)
       delay(3000);

       Serial.println("M0: Stop");
       analogWrite(motorPwmPin, 0);       // Stop the motor
       delay(1000);

       Serial.println("M0: Reverse 50%");
       digitalWrite(motorDirPin, LOW);    // Reverse direction
       analogWrite(motorPwmPin, 128);     // ~50% speed
       delay(3000);

       Serial.println("M0: Stop");
       analogWrite(motorPwmPin, 0);       // Stop the motor
       delay(3000);
   }

**How it Works**

This lesson drives the motor the direct way: two ordinary pins and the same ``digitalWrite()`` and ``analogWrite()`` functions you already know. One pin tells the Robot Shield's H-bridge which way current should flow, and the other sets how much power the motor gets. No library needed — just plain Arduino:

.. code-block:: text

   setup() → runs once at startup:
       Start Serial Monitor
       Set direction pin D4 as OUTPUT
       Set PWM pin D5 as OUTPUT
       Motor starts stopped (PWM = 0)

   loop() → runs over and over forever:
       Forward (direction HIGH, speed 128) → wait 3 seconds
       Stop (PWM = 0)                      → wait 1 second
       Reverse (direction LOW, speed 128)  → wait 3 seconds
       Stop (PWM = 0)                      → wait 3 seconds
       (repeat)

#. Direction and Speed Pin Constants

   - Two ``const int`` names make the pin numbers easy to remember and change
   - ``motorDirPin = 4`` is the **direction** pin — the H-bridge on the Robot Shield reads it to decide which way current flows through the motor
   - ``motorPwmPin = 5`` is the **PWM** pin — it sets the motor's speed

   .. code-block:: arduino

      const int motorDirPin = 4;  // Motor direction control
      const int motorPwmPin = 5;  // Motor speed control (PWM)

#. Setup: Configuring the Pins

   - Both pins are declared ``OUTPUT`` — the same ``pinMode()`` pattern you used with LEDs earlier
   - ``analogWrite(motorPwmPin, 0)`` starts the motor stopped, so it doesn't spin the moment the app runs
   - There is no library to initialize — a DC motor needs only these two lines

   .. code-block:: arduino

      void setup() {
          Serial.begin(115200);
          pinMode(motorDirPin, OUTPUT);
          pinMode(motorPwmPin, OUTPUT);
          analogWrite(motorPwmPin, 0);  // Motor starts stopped
      }

#. Motor Speed and Direction in the Loop

   - ``digitalWrite(motorDirPin, HIGH)`` spins the motor forward; ``LOW`` spins it in reverse — this is the digital signal that tells the H-bridge which way current should flow
   - ``analogWrite(motorPwmPin, value)`` sets the speed from 0 to 255 — ``128`` is about 50%, and ``0`` stops the motor
   - The ``delay()`` calls keep each state active long enough for you to observe the motion

   .. code-block:: arduino

      digitalWrite(motorDirPin, HIGH);   // Forward direction
      analogWrite(motorPwmPin, 128);     // ~50% speed (0-255)
      delay(3000);

      analogWrite(motorPwmPin, 0);       // Stop the motor
      delay(1000);

      digitalWrite(motorDirPin, LOW);    // Reverse direction
      analogWrite(motorPwmPin, 128);     // ~50% speed
      delay(3000);

      analogWrite(motorPwmPin, 0);       // Stop the motor
      delay(3000);


3. Experiment
----------------

**Change Speed and Direction**

Try different speed values and observe how the motor responds:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - ``analogWrite(motorPwmPin, value)``
     - Motor Behavior
   * - ``analogWrite(motorPwmPin, 255)``
     - Full speed forward — strongest airflow from the fan
   * - ``analogWrite(motorPwmPin, 64)``
     - Slow forward — gentle breeze (~25% speed)
   * - ``digitalWrite(motorDirPin, LOW)`` + ``analogWrite(motorPwmPin, 255)``
     - Full speed reverse — airflow direction flips
   * - ``analogWrite(motorPwmPin, 26)``
     - Barely spinning — the lowest speed that overcomes friction (~10%)

Try values between 26 and 51 (about 10–20% of 255) to find the **minimum starting speed** — the point where the motor just begins to turn. This threshold exists because the motor must overcome static friction before it can spin.

**Challenge: Ramp Up and Down**

Instead of jumping instantly to full speed, make the motor **ramp up** from 0 to 255 and then **ramp down** from 255 to 0. This creates a smooth acceleration and deceleration — like a fan spinning up and winding down.

.. dropdown:: Click to reveal solution
   :open:

   .. code-block:: cpp

      void loop() {
          // Ramp up: 0 → 255
          for (int speed = 0; speed <= 255; speed += 13) {
              analogWrite(motorPwmPin, speed);
              Serial.print("Forward: ");
              Serial.println(speed);
              delay(100);
          }
          delay(1000);  // Hold at full speed

          // Ramp down: 255 → 0
          for (int speed = 255; speed >= 0; speed -= 13) {
              analogWrite(motorPwmPin, speed);
              Serial.print("Slowing: ");
              Serial.println(speed);
              delay(100);
          }
          delay(2000);  // Pause before repeating
      }

   The ``speed += 13`` in each loop iteration increases the speed by about 5% (13 out of 255) every 100ms — it takes about 2 seconds to go from 0 to 255. Change the step size (``13`` → ``5``) for a smoother but slower ramp, or (``13`` → ``25``) for a faster, jumpier one.


4. Troubleshooting
--------------------

**Motor does not spin at all**

* **Cause:** The battery is not connected or depleted, or the motor connector is loose.
* **Solution:** Check that the battery pack is connected and has fresh batteries. Verify the motor connector is firmly seated in the M0 terminal.

**Motor hums but doesn't turn**

* **Cause:** The PWM value is too low to overcome static friction, or something is blocking the shaft.
* **Solution:** Increase the PWM value to at least 77–102 (about 30–40% of 255). Every motor has a minimum starting threshold. Check that nothing is touching the motor shaft or fan blade.

**Motor only spins in one direction**

* **Cause:** The code never changes the direction pin.
* **Solution:** Make sure the code toggles ``digitalWrite(motorDirPin, ...)`` between HIGH and LOW. Check that your ``delay()`` values are long enough to notice the change — a reversed motor at 50% looks identical to a forward motor if you blink.

5. Summary
-------------

You just made something move — and that's a big deal. DC motors are the foundation of robotics, drones, electric vehicles, and industrial automation. In this lesson, you learned:

* How to control a DC motor with a direction pin (D4) and a PWM pin (D5)
* How ``analogWrite()`` sets the speed (0–255) while a digital pin picks the direction
* How an H-bridge reverses motor polarity to change direction
* Why motors need a separate battery — logic power and motor power are independent
* How to ramp speed smoothly with ``for`` loops and ``analogWrite()``

In the next lesson, you'll control a different kind of motor — a **servo** that moves to precise angles instead of spinning continuously. Servos are how robots achieve precise positioning: steering, pan-tilt camera mounts, and robotic arms.
