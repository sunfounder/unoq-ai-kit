.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

03 Tilt Alarm
======================

In the last two lessons, you controlled an LED and read a button. Now you'll combine those skills to build something practical — a **tilt alarm** that sounds a buzzer when the device tips over.

In this lesson, you will learn to:

* Read a tilt switch as a digital input (it's just a mechanical switch — same ``INPUT_PULLUP`` pattern as the button)
* Control an active buzzer as a digital output
* Use a debounce technique to filter out false triggers from mechanical switches
* Create a rhythmic alarm pattern by sequencing ``delay()`` calls

1. Build the Circuit
----------------------

**Components Needed**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_tilt_switch`
     - 1 * Active :ref:`cpn_buzzer`
     - Several :ref:`cpn_wires`
   * - |list_pan_tilt|
     - |list_tilt_switch|
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

.. tip::

   No external resistor is needed for either component. The tilt switch uses ``INPUT_PULLUP`` (just like the button you used earlier), and the active buzzer has its own internal circuitry. If your buzzer has a sticker covering the top, peel it off before use — it protects the sound hole during shipping.

**Wiring Diagram**

Follow the diagram below to place each component on the breadboard and connect the wires.

.. image:: /img/wiring/wiring_tilt_buzzer.png
   :width: 500
   :align: center

.. warning::

   The active buzzer has **polarity** — it only works in one direction. Check that the pin labeled **+** (or the longer leg) connects to pin 5, and the pin labeled **−** (or the shorter leg) connects to GND. Reversing it won't damage the buzzer, but it won't make any sound.

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


#. Navigate to the ``unoq-ai-kit/basic/`` folder and select ``03 Tilt Alarm.zip``. The app appears in **My Apps** — click it to open.

#. With the app open, click the **Run** button (▶) in the top-right corner.

   .. image:: /img/app_run.png
      :width: 500


#. Wait a few seconds for the upload to finish, then keep the breadboard flat — the buzzer should be silent. Now tilt it — the buzzer sounds a rhythmic alarm. Straighten it again — the alarm stops.

**The Sketch (sketch.ino)**

Now that you've heard the alarm in action, let's look at the sketch file that makes it work.

.. code-block:: cpp
   :linenos:

   /*
    * Sounds a rhythmic alarm when the device is tilted.
    */

   const int tiltPin = 2;    // Tilt switch connected to pin 2
   const int buzzerPin = 5;  // Active buzzer connected to pin 5

   void setup() {
       pinMode(tiltPin, INPUT_PULLUP);  // Tilt switch: closed → LOW, open → HIGH
       pinMode(buzzerPin, OUTPUT);
       digitalWrite(buzzerPin, LOW);    // Start with buzzer off
   }

   void loop() {
       int tiltState = digitalRead(tiltPin);

       // Tilted? (switch open → pin reads HIGH)
       if (tiltState == HIGH) {
           delay(30);  // Simple debounce: wait and re-check

           if (digitalRead(tiltPin) == HIGH) {
               // Rhythmic alarm: two short beeps, one long beep
               digitalWrite(buzzerPin, HIGH);
               delay(100);
               digitalWrite(buzzerPin, LOW);
               delay(100);

               digitalWrite(buzzerPin, HIGH);
               delay(300);
               digitalWrite(buzzerPin, LOW);
               delay(200);
           }
       } else {
           digitalWrite(buzzerPin, LOW);  // Upright → silent
       }
   }

**How it Works**

This lesson introduces debounce — a technique for handling the noisy, bouncy behavior of mechanical switches:

.. code-block:: text

   setup() → runs once at startup:
       Configure pin 2 as INPUT_PULLUP (tilt switch input)
       Configure pin 5 as OUTPUT (buzzer control)
       Set buzzer to LOW (silent on startup)

   loop() → runs over and over forever:
       Read tilt switch
           Tilted (HIGH)?
               YES → wait 30ms → check again → still tilted?
                   YES → sound rhythmic alarm pattern
                   NO  → false alarm, ignore
               NO  → buzzer stays OFF

#. Pin Configuration and Initialization

   - The tilt switch uses ``INPUT_PULLUP`` — the pin reads HIGH when open (tilted) and LOW when closed (upright)
   - The buzzer pin is set as ``OUTPUT`` and explicitly turned off in ``setup()`` to prevent unexpected beeps at startup

   .. code-block:: arduino

      const int tiltPin = 2;
      const int buzzerPin = 5;

      void setup() {
          pinMode(tiltPin, INPUT_PULLUP);
          pinMode(buzzerPin, OUTPUT);
          digitalWrite(buzzerPin, LOW);
      }

#. Reading the Tilt Switch with Debounce

   - When ``digitalRead()`` detects the switch is open (tilted), the code waits 30 ms and reads again
   - This is **debounce**: mechanical switches vibrate when changing state, causing rapid HIGH/LOW fluctuations
   - The short delay and second read filter out false triggers so a single jolt does not set off the alarm

   .. code-block:: arduino

      int tiltState = digitalRead(tiltPin);

      if (tiltState == HIGH) {
          delay(30);

          if (digitalRead(tiltPin) == HIGH) {

#. The Rhythmic Alarm Pattern

   - Instead of a constant tone, the code creates a pattern of two short beeps followed by one long beep
   - Each ``digitalWrite()`` / ``delay()`` pair is one note in the rhythm
   - Change the delay values to create faster beeps or longer, drawn-out tones

   .. code-block:: arduino

      digitalWrite(buzzerPin, HIGH);
      delay(100);
      digitalWrite(buzzerPin, LOW);
      delay(100);

      digitalWrite(buzzerPin, HIGH);
      delay(300);
      digitalWrite(buzzerPin, LOW);
      delay(200);

#. Staying Silent When Upright

   - The ``else`` branch ensures the buzzer turns off immediately when the device returns upright
   - Without it, the alarm pattern would continue its current cycle even after straightening the device

   .. code-block:: arduino

      } else {
          digitalWrite(buzzerPin, LOW);
      }

3. Experiment
----------------

**Change the Alarm Pattern**

Try modifying the delay values to create different rhythms:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Pattern
     - Code
   * - Constant fast beep
     - ON ``delay(50)``, OFF ``delay(50)``
   * - Two-tone siren
     - ON ``delay(200)``, OFF ``delay(100)``, ON ``delay(500)``, OFF ``delay(200)``
   * - Single long alarm
     - ON ``delay(1000)``, OFF ``delay(500)``
   * - Triple beep
     - Three ON ``delay(100)`` / OFF ``delay(80)`` pairs, then OFF ``delay(400)``


**Challenge: Sensitivity Tuning**

What happens if you increase the debounce delay from 30ms to 100ms? Or decrease it to 10ms? Try each and observe how the alarm responds to gentle tilts vs. sharp shakes. Which value feels most reliable?

4. Troubleshooting
--------------------

**Buzzer does not make any sound**

* **Cause:** The buzzer's protective sticker is still on, or the polarity is reversed.
* **Solution:** Peel off the sticker covering the buzzer's sound hole. Check that the **+** pin (or longer leg) connects to pin 5 and the **−** pin (or shorter leg) connects to GND. The active buzzer has polarity — it won't work backwards.

**Alarm sounds even when the device is upright**

* **Cause:** The tilt switch is installed upside down or sideways, so it's already open.
* **Solution:** The tilt switch used in this lesson is **closed when upright** (the internal ball bridges the contacts) and **open when tilted**. If yours behaves opposite, swap ``HIGH`` and ``LOW`` in the ``if`` condition, or rotate the switch 180° on the breadboard.

**Alarm triggers too easily (false alarms)**

* **Cause:** The debounce delay is too short, or the device is on an unstable surface.
* **Solution:** Increase the debounce delay from ``30`` to ``50`` or even ``100`` ms. This makes the alarm less sensitive to minor vibrations and accidental bumps.

**Buzzer sounds very quietly**

* **Cause:** The active buzzer may require more current than a digital pin can supply comfortably.
* **Solution:** Most active buzzers in this kit work fine directly from a pin. If yours is quiet, a transistor driver circuit can provide more current — this is covered in a later lesson.


* **Cause:** The board is not connected, or App Lab can't find it.
* **Solution:** Check the USB-C cable is firmly connected at both ends. Try unplugging and re-plugging it. In App Lab, make sure your UNO Q is detected.

5. Summary
-------------

Congratulations! You've built a working alarm system — your most practical project yet. In this lesson, you learned:

* How a tilt switch works as a mechanical orientation sensor (same ``INPUT_PULLUP`` principle as a button)
* How to control an active buzzer as a simple on/off sound output
* What switch "bounce" is and how a small delay filters it out for reliable readings
* How to combine timing delays into rhythmic patterns for more expressive output
* How to synchronize multiple outputs (buzzer + LED) in a single program

You now know how to read digital sensors, control digital actuators, and link them with decision logic. In the next lesson, you'll move beyond digital on/off signals and enter the world of **analog** input — using a potentiometer to smoothly control LED brightness.
