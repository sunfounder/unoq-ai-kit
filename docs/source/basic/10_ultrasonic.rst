.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

10 Ultrasonic Radar
=====================

Bats fly in complete darkness without crashing — they emit high-pitched sounds and listen for the echoes to "see" their surroundings. In this lesson, you'll use the same principle with an **ultrasonic sensor** (HC-SR04) to build a parking radar: it measures how far away an object is and beeps faster as you get closer. No more crashing into things — your circuit now has sonar.

In this lesson, you will learn to:

* Wire and use an HC-SR04 ultrasonic distance sensor
* Use ``pulseIn()`` to measure how long a pulse stays HIGH, in microseconds
* Convert a sound wave's round-trip time into a physical distance in centimeters
* Build a multi-level alarm system that changes behavior based on distance

1. Setup
----------------------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_ultrasonic_sensor`
     - 1 * Active :ref:`cpn_buzzer`
     - Several :ref:`cpn_wires`
   * - |list_pan_tilt|
     - |list_ultrasonic|
     - |list_active_buzzer|
     - |list_wire|
   * - 1 * :ref:`cpn_breadboard`
     - 1 * USB Cable
     -
     -
   * - |list_breadboard|
     - |list_usb_cable|
     -
     -

**Software Requirements**

This project uses no external libraries — the sketch only uses the built-in Arduino framework.

**Wiring Diagram**

Connect the HC-SR04's **VCC to 3.3V**, **Trig to pin 3**, **Echo to pin 2**, and **GND to GND** (leave any jumper cap on the sensor's back in place), and connect the active buzzer's **+ pin to D5** and **− pin to GND** — swapping Trig and Echo is the most common wiring mistake, so double-check these two wires.

.. image:: /img/wiring/wiring_ultrasonic.png
   :width: 500
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


#. Navigate to the ``unoq-ai-kit/basic/`` folder and select ``10 Ultrasonic Radar.zip``. The app appears in **Apps** — click it to open.

#. With the app open, click the **Run** button (▶) in the top-right corner.

   .. image:: /img/app_run.png
      :width: 500


#. Wait a few seconds for the upload to finish, then open the **Serial Monitor** (📊 icon). Move your hand slowly toward and away from the ultrasonic sensor — you'll see distance readings in centimeters, and the buzzer will beep progressively faster as your hand gets closer. Below 20 cm, it beeps urgently.

**The Sketch (sketch.ino)**

Now that you've seen the radar in action, let's look at the sketch file that measures distance with sound.

.. code-block:: cpp
   :linenos:

   /*
    * Measures distance and beeps faster as obstacles get closer.
    */

   const int trigPin = 3;     // Trigger pin
   const int echoPin = 2;     // Echo pin
   const int buzzerPin = 5;   // Active buzzer

   long duration;
   float distanceCm;

   void setup() {
       Serial.begin(115200);

       pinMode(trigPin, OUTPUT);
       pinMode(echoPin, INPUT);
       pinMode(buzzerPin, OUTPUT);

       digitalWrite(trigPin, LOW);
       digitalWrite(buzzerPin, LOW);
   }

   float getDistance() {
       digitalWrite(trigPin, LOW);
       delayMicroseconds(2);
       digitalWrite(trigPin, HIGH);
       delayMicroseconds(10);     // 10 µs trigger pulse
       digitalWrite(trigPin, LOW);

       duration = pulseIn(echoPin, HIGH, 30000);  // 30 ms timeout

       if (duration == 0) return -1;  // No echo received

       return duration * 0.0343 / 2;  // Convert to cm
   }

   void beepOnce(int onTime, int offTime) {
       digitalWrite(buzzerPin, HIGH);
       delay(onTime);
       digitalWrite(buzzerPin, LOW);
       delay(offTime);
   }

   void loop() {
       distanceCm = getDistance();

       Serial.print("Distance: ");
       if (distanceCm < 0) {
           Serial.println("Out of range");
           digitalWrite(buzzerPin, LOW);
           delay(300);
           return;
       } else {
           Serial.print(distanceCm);
           Serial.println(" cm");
       }

       if (distanceCm > 100) {
           digitalWrite(buzzerPin, LOW);  // Safe — no alarm
           delay(300);
       } else if (distanceCm > 50) {
           beepOnce(100, 500);             // Slow beep
       } else if (distanceCm > 20) {
           beepOnce(100, 250);             // Medium beep
       } else {
           beepOnce(100, 100);             // Fast urgent beep
       }
   }

**How it Works**

This lesson introduces three new tools — microsecond timing with ``pulseIn()``, a custom ``getDistance()`` function that returns a calculated value, and a multi-level decision chain:

.. code-block:: text

   setup() → runs once at startup:
       Configure Trig pin as OUTPUT (sends trigger pulse)
       Configure Echo pin as INPUT (reads echo pulse)
       Configure buzzer as OUTPUT, set both pins LOW

   loop() → runs over and over forever:
       Call getDistance() → returns distance in cm (or -1 if no echo)
       Print distance to Serial Monitor
       If out of range → buzzer OFF, wait 300ms
       If > 100 cm → safe zone, no alarm
       If 50–100 cm → slow beep (caution)
       If 20–50 cm  → medium beep (warning)
       If < 20 cm   → fast urgent beep (danger!)
       (repeat — checks distance continuously)

#. Global Variables and Pin Declarations

   - The Trig pin sends the ultrasonic pulse, the Echo pin listens for the returning echo, and the buzzer sounds the alarm
   - ``duration`` and ``distanceCm`` are global variables that carry measurement results between functions

   .. code-block:: arduino

      const int trigPin = 3;
      const int echoPin = 2;
      const int buzzerPin = 5;

      long duration;
      float distanceCm;

#. The ``getDistance()`` Function: Sending a Trigger Pulse

   - The function starts by sending a 10-microsecond HIGH pulse on the Trig pin
   - This short burst instructs the HC-SR04 to emit eight 40 kHz ultrasonic pulses
   - The sensor handles the actual sound generation — your code just provides the trigger signal

   .. code-block:: arduino

      float getDistance() {
          digitalWrite(trigPin, LOW);
          delayMicroseconds(2);
          digitalWrite(trigPin, HIGH);
          delayMicroseconds(10);
          digitalWrite(trigPin, LOW);

#. The ``getDistance()`` Function: Measuring the Echo and Converting to Distance

   - ``pulseIn()`` waits for the Echo pin to go HIGH and measures how many microseconds it stays HIGH — the round-trip time of the sound wave
   - The third argument (30000) is a timeout: if no echo arrives within 30 ms, the function returns -1 for "out of range"
   - Distance is calculated by multiplying echo time by the speed of sound (0.0343 cm/µs) and dividing by 2 for the one-way trip

   .. code-block:: arduino

          duration = pulseIn(echoPin, HIGH, 30000);

          if (duration == 0) return -1;

          return duration * 0.0343 / 2;
      }

#. Multi-Level Alarm Zones in the Loop

   - The ``if / else if / else`` chain creates four distinct alarm zones checked from top to bottom
   - Beyond 100 cm the buzzer stays silent (safe zone), between 50–100 cm it beeps slowly (caution), between 20–50 cm it beeps at a medium rate (warning), and below 20 cm it beeps urgently (danger)

   .. code-block:: arduino

      if (distanceCm > 100) {
          digitalWrite(buzzerPin, LOW);
          delay(300);
      } else if (distanceCm > 50) {
          beepOnce(100, 500);
      } else if (distanceCm > 20) {
          beepOnce(100, 250);
      } else {
          beepOnce(100, 100);
      }

3. Experiment
----------------

**Adjust the Thresholds**

Try changing the distance thresholds and observe how the radar responds:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Threshold Change
     - Effect
   * - ``50`` → ``30``, ``20`` → ``10``
     - Shrinks warning zone — beeps only when very close (like a parking sensor)
   * - ``100`` → ``200``, ``50`` → ``100``, ``20`` → ``50``
     - Expands detection range — warns from much farther away (like a security perimeter)
   * - Single threshold (only ``< 30`` beeps)
     - Binary alarm — either silent or urgent, nothing in between
   * - Add a 5th zone (e.g., ``< 10`` cm constant tone)
     - Extra urgency for extremely close objects — continuous buzzer instead of beeps


4. Troubleshooting
--------------------

**Distance always shows "Out of range"**

* **Cause:** The Trig and Echo pins are swapped, or the module isn't receiving power.
* **Solution:** Double-check: Trig → pin 3, Echo → pin 2, VCC → 3.3V, GND → GND. Swapping Trig and Echo is the most common wiring mistake with this sensor. Also verify the breadboard power rails are connected.

**Distance readings are consistently too high or too low**

* **Cause:** The sensor is pointed at a soft, angled, or irregular surface that absorbs or scatters sound.
* **Solution:** Ultrasonic sensors work best with hard, flat surfaces perpendicular to the sensor — like a wall or your palm held flat. Soft fabrics, acoustic foam, and angled surfaces give weak or misleading echoes. Test with a book held flat, facing the sensor.

**Readings jump between a valid distance and "Out of range"**

* **Cause:** The object is near the edge of the sensor's 15° detection cone, and small movements cause the echo to miss the receiver.
* **Solution:** Make sure the object is directly in front of the sensor, within a 15° cone. For more stable readings, try taking 3 quick measurements and using the middle (median) value — this filters out sporadic dropouts.

**Minimum distance is stuck at 2–3 cm, never lower**

* **Cause:** This is normal — the HC-SR04 has a minimum sensing range of about 2 cm. Below that, the outgoing pulse hasn't finished transmitting before the echo returns.
* **Solution:** For detecting objects closer than 2 cm, use an infrared proximity sensor (covered in a later lesson). The 2 cm minimum is a physical limitation of ultrasonic technology, not a bug in your code.

5. Summary
-------------

You've built a working sonar — a device that sees with sound. In this lesson, you learned:

* How an ultrasonic sensor uses 40 kHz sound waves to measure distance without contact
* How ``pulseIn()`` measures microsecond-precision pulse durations
* How to convert an echo time into centimeters using the speed of sound
* How to return values from functions with ``return`` — making your code modular and reusable
* How to chain ``if / else if / else`` to create multiple behavior zones based on distance

With ultrasonic sensing, your projects can now perceive the physical world beyond simple on/off states. In the next lesson, you'll add environmental sensing — using the DHT11 to measure **temperature and humidity**, bringing data logging and climate awareness to your toolkit.
