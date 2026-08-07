.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

07 Motor Speed Controller
==============

LEDs, buzzers, and sensors are all about light, sound, and data — but what about **motion**? In this lesson, you'll control your first actuator that physically moves: a **DC motor**. Spin it forward to blow air with a fan blade, reverse it to change direction, and vary the speed from a gentle breeze to full blast. Motors are the muscles of robotics — and you're about to make something move.

In this lesson, you will learn to:

* Control a DC motor with the RobotShield ``Motor`` class
* Set motor **speed** with PWM power levels (0–100%)
* Control motor **direction** with positive and negative power values
* Understand why motors need a **separate power source** (battery) — USB alone isn't enough

1. Build the Circuit
----------------------

**Components Needed**

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

**Wiring Diagram**


.. image:: img/wiring_motor.png
   :width: 600
   :align: center

.. warning::

**Circuit Diagram**

The Robot Shield's onboard MCU receives commands via I2C from the STM32 and drives the motor through an H-bridge — a circuit that can reverse the voltage polarity to change motor direction.

.. image:: img/sche_7_motor.png
   :width: 500
   :align: center

The ``Motor`` class in the code sends commands to the Robot Shield, which handles the power delivery. Inside the Robot Shield, an H-bridge controls both speed (via PWM) and direction (by reversing voltage polarity):

  **Positive power → current flows one way → motor spins forward**

  **Negative power → voltage polarity reversed → motor spins backward**

  **Zero power → H-bridge shorts motor terminals → motor brakes (stops quickly)**

2. Code
----------

**Import and Run the Code**

All code for this course is provided as ``.zip`` files that you can import directly into App Lab.

#. Open **Arduino App Lab**, go to **My Apps**. Click the dropdown arrow next to **Create new app +** and select **Import App**.

   .. image:: img/app_import_app.png
      :width: 600


#. Select **Import from Computer**.

   .. image:: img/app_import_pc.png
      :width: 600


#. Navigate to the ``unoq-ai-kit/basic/`` folder and select ``07 Motor Speed Controller.zip``. The app appears in **My Apps** — click it to open.

#. With the app open, click the **Run** button (▶) in the top-right corner.

   .. note::      
      
      This project uses the **RobotShield** library. see :ref:`install_update_lib_c` for installation or updating.
   
   .. image:: img/app_run.png
      :width: 500


#. Wait a few seconds for the upload to finish. The motor should spin **forward for 3 seconds**, brake for 1 second, spin **backward for 3 seconds**, then brake for 3 seconds — repeating this cycle indefinitely. If you attached the fan blade, you'll feel the airflow change direction.

**The Sketch (sketch.ino)**

Now that you've seen the motor in action, let's look at the sketch file.

.. code-block:: cpp
   :linenos:

   /*
    * Drives a DC motor on M0: forward → brake → reverse → brake.
    */

   #include "RobotShield.h"

   Motor motor("M0", 4, 5);  // Motor on port M0, direction pins 4 and 5

   void setup() {
       Serial.begin(115200);
       I2cBus::i2c().begin();
       motor.begin();

       Serial.println("=== MotorTest Ready ===");
   }

   void loop() {
       Serial.println("M0: Forward 50%");
       motor.setPower(50);      // Forward at 50% power
       delay(3000);

       Serial.println("M0: Brake");
       motor.setPower(0);       // Stop (brake)
       delay(1000);

       Serial.println("M0: Reverse 50%");
       motor.setPower(-50);     // Reverse at 50% power
       delay(3000);

       Serial.println("M0: Brake");
       motor.setPower(0);       // Stop (brake)
       delay(3000);
   }

**How it Works**

This lesson introduces the ``Motor`` class — a completely new kind of output. Motors convert electrical power into rotational motion, and the RobotShield's H-bridge gives you precise control over both speed and direction:

.. code-block:: text

   setup() → runs once at startup:
       Start Serial Monitor
       Initialize I2C bus (Robot Shield communication)
       Initialize motor on port M0

   loop() → runs over and over forever:
       Set motor forward at 50% → wait 3 seconds
       Brake (stop motor)        → wait 1 second
       Set motor reverse at 50%  → wait 3 seconds
       Brake (stop motor)        → wait 3 seconds
       (repeat)

#. Library Include and Motor Object Declaration

   - The ``RobotShield.h`` library provides the ``Motor`` class for controlling DC motors
   - ``Motor motor("M0", 4, 5)`` creates a motor object on port **M0** — the Robot Shield has two ports, M0 and M1
   - The numbers ``4`` and ``5`` are direction control pins that tell the H-bridge which way current should flow

   .. code-block:: arduino

      #include "RobotShield.h"
      Motor motor("M0", 4, 5);

#. Setup: Initializing the Motor Driver

   - After starting the Serial Monitor and I2C bus, ``motor.begin()`` initializes the motor driver
   - This must be called in ``setup()`` before you can use ``setPower()``
   - This follows the same initialization pattern used with the ``Pwm`` class in Lesson 5

   .. code-block:: arduino

      void setup() {
          Serial.begin(115200);
          I2cBus::i2c().begin();
          motor.begin();
      }

#. Motor Speed and Direction in the Loop

   - ``motor.setPower()`` accepts a percentage from -100 to 100
   - Positive values spin the motor forward, zero applies the brake (shorting the terminals for a quick stop), and negative values spin it in reverse
   - The ``delay()`` calls keep each state active long enough for you to observe the motion

   .. code-block:: arduino

      motor.setPower(50);      // Forward at 50% power
      delay(3000);

      motor.setPower(0);       // Stop (brake)
      delay(1000);

      motor.setPower(-50);     // Reverse at 50% power
      delay(3000);

      motor.setPower(0);       // Stop (brake)
      delay(3000);


3. Experiment
----------------

**Change Speed and Direction**

Try different power levels and observe how the motor responds:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - ``setPower()`` Value
     - Motor Behavior
   * - ``motor.setPower(100)``
     - Full speed forward — strongest airflow from the fan
   * - ``motor.setPower(25)``
     - Slow forward — gentle breeze
   * - ``motor.setPower(-100)``
     - Full speed reverse — airflow direction flips
   * - ``motor.setPower(10)``
     - Barely spinning — the lowest power that overcomes friction

Try values between 10 and 20 to find the **minimum starting power** — the point where the motor just begins to turn. This threshold exists because the motor must overcome static friction before it can spin.

**Challenge: Ramp Up and Down**

Instead of jumping instantly to full speed, make the motor **ramp up** from 0 to 100 and then **ramp down** from 100 to 0. This creates a smooth acceleration and deceleration — like a fan spinning up and winding down.

.. dropdown:: Click to reveal solution
   :open:

   .. code-block:: cpp

      void loop() {
          // Ramp up: 0 → 100
          for (int power = 0; power <= 100; power += 5) {
              motor.setPower(power);
              Serial.print("Forward: ");
              Serial.println(power);
              delay(100);
          }
          delay(1000);  // Hold at full speed

          // Ramp down: 100 → 0
          for (int power = 100; power >= 0; power -= 5) {
              motor.setPower(power);
              Serial.print("Slowing: ");
              Serial.println(power);
              delay(100);
          }
          delay(2000);  // Pause before repeating
      }

   The ``power += 5`` in each loop iteration increases the power by 5% every 100ms — it takes about 2 seconds to go from 0 to 100. Change the step size (``5`` → ``2``) for a smoother but slower ramp, or (``5`` → ``20``) for a faster, jumpier one.


4. Troubleshooting
--------------------

**Motor does not spin at all**

* **Cause:** The battery is not connected or depleted, or the motor connector is loose.
* **Solution:** Check that the battery pack is connected and has fresh batteries. Verify the motor connector is firmly seated in the M0 terminal.

**Motor hums but doesn't turn**

* **Cause:** The power level is too low to overcome static friction, or something is blocking the shaft.
* **Solution:** Increase the power to at least 30–40%. Every motor has a minimum starting threshold. Check that nothing is touching the motor shaft or fan blade.

**Motor only spins in one direction**

* **Cause:** The code only uses positive (or only negative) power values.
* **Solution:** Make sure ``setPower()`` receives both positive and negative values. Check that your ``delay()`` values are long enough to notice the change — a reversed motor at 50% looks identical to a forward motor if you blink.


* **Cause:** The board is not connected, or App Lab can't find it.
* **Solution:** Check the USB-C cable is firmly connected at both ends. Try unplugging and re-plugging it. In App Lab, make sure your UNO Q is detected.

5. Summary
-------------

You just made something move — and that's a big deal. DC motors are the foundation of robotics, drones, electric vehicles, and industrial automation. In this lesson, you learned:

* How to control a DC motor with the RobotShield ``Motor`` class
* How ``setPower()`` controls both speed (0–100%) and direction (positive/negative)
* How an H-bridge reverses motor polarity to change direction
* Why motors need a separate battery — logic power and motor power are independent
* How to ramp speed smoothly with ``for`` loops and ``map()``

In the next lesson, you'll control a different kind of motor — a **servo** that moves to precise angles instead of spinning continuously. Servos are how robots achieve precise positioning: steering, pan-tilt camera mounts, and robotic arms.
