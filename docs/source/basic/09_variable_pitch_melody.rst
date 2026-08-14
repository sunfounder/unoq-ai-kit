.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

09 Variable Pitch Melody
========================

Earlier, you used a photoresistor to read light levels — your first analog sensor. Now you'll use a **potentiometer** to control a passive buzzer — not just a single tone, but a repeating four-note melody. Turn the knob one way and the entire melody shifts higher; turn it the other way and it drops lower. The musical intervals stay intact — the tune is recognizable at any pitch.

In this lesson, you will learn to:

* Apply ``analogRead()`` with a new sensor — the potentiometer
* Control a passive buzzer's **frequency** with PWM
* Use the ``map()`` function to convert potentiometer readings into a pitch percentage
* Store a melody in an **array** and play notes in sequence
* Calculate the relationship between **frequency**, **period**, and **duty cycle**

1. Build the Circuit
----------------------

**Components Needed**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_potentiometer`
     - 1 * Passive :ref:`cpn_buzzer`
     - Several :ref:`cpn_wires`
   * - |list_pan_tilt_kit|
     - |list_potentiometer|
     - |list_passive_buzzer|
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

   A **passive buzzer** is different from the active buzzer you've used before. An active buzzer has a built-in oscillator — you just apply DC voltage and it beeps at a fixed frequency. A passive buzzer has no internal oscillator — you must supply an AC signal (a square wave from PWM) to make it vibrate. This gives you control over the **pitch** (frequency), which is exactly what we need for this lesson. The potentiometer has three pins — the middle pin is the **wiper** (variable output), and the two outer pins connect to 3.3V and GND.

**Wiring Diagram**

Follow the diagram below to place each component on the breadboard and connect the wires.

A passive buzzer has **no polarity** — you can connect it either way. However, the potentiometer's three pins are not interchangeable. Connect the **left pin to 3.3V**, the **middle pin to A2**, and the **right pin to GND**. Reversing 3.3V and GND won't damage the potentiometer, but the knob will behave backwards (clockwise lowers the pitch instead of raising it).

.. image:: /img/wiring/wiring_pot_buzzer.png
   :width: 500
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

#. Navigate to the ``unoq-ai-kit/basic/`` folder and select ``09 Variable Pitch Melody.zip``. The app appears in **My Apps** — click it to open.

#. With the app open, click the **Run** button (▶) in the top-right corner.

   .. note::

      This project uses the **RobotShield** library. see :ref:`install_update_lib_c` for installation or updating.

   .. image:: /img/app_run.png
      :width: 500

#. Wait a few seconds for the upload to finish, then open the **Serial Monitor** (📊 icon in the top bar). You should hear a repeating four-note melody. Turn the potentiometer — the entire melody shifts higher or lower while keeping the same tune. Open the Serial Monitor to see the current frequency.

**The Sketch (sketch.ino)**

Now that you've heard the melody change pitch, let's look at the sketch file.

.. code-block:: cpp
   :linenos:

   #include "RobotShield.h"

   const int POT_PIN = A2;
   const int MIN_PITCH_PERCENT = 50;
   const int MAX_PITCH_PERCENT = 200;
   const int NOTE_DURATION = 250;
   const int NOTE_GAP = 50;

   const uint16_t MELODY[] = {262, 330, 392, 523};  // C4, E4, G4, C5
   const int MELODY_LENGTH = sizeof(MELODY) / sizeof(MELODY[0]);

   Pwm buzzer(5);

   void playFrequency(uint16_t frequency) {
       uint32_t period = 1000000UL / frequency;
       uint16_t pulse = period / 2;
       buzzer.setEnable(false);
       buzzer.setFreq(frequency);
       buzzer.setPulse(pulse);
       buzzer.setEnable(true);
   }

   void stopBuzzer() { buzzer.setEnable(false); }

   void setup() {
       Serial.begin(115200);
       I2cBus::i2c().begin();
       buzzer.begin();
       buzzer.setEnable(false);
       Serial.println("=== Variable Pitch Melody ===");
   }

   void loop() {
       for (int note = 0; note < MELODY_LENGTH; note++) {
           int potValue = analogRead(POT_PIN);
           int pitchPercent = map(potValue, 0, 1023,
                                  MIN_PITCH_PERCENT, MAX_PITCH_PERCENT);
           uint16_t frequency =
               (uint32_t)MELODY[note] * pitchPercent / 100;

           playFrequency(frequency);

           Serial.print("Pot: "); Serial.print(potValue);
           Serial.print("  Pitch: "); Serial.print(pitchPercent);
           Serial.print("%  Freq: "); Serial.print(frequency);
           Serial.println(" Hz");

           delay(NOTE_DURATION);
           stopBuzzer();
           delay(NOTE_GAP);
       }
   }

**How it Works**

This lesson introduces three new ideas — a melody stored in an array, pitch control via the potentiometer, and PWM frequency generation — working together:

.. code-block:: text

   setup() → runs once at startup:
       Start Serial Monitor
       Initialize I2C bus (Robot Shield communication)
       Initialize PWM channel on P5, start disabled

   loop() → runs over and over forever:
       For each note in the melody:
           Read potentiometer on A2 (0–1023)
           Map to pitch percentage (50–200%)
           Multiply note frequency by pitch percentage
           Play the note for 250ms
           Silence for 50ms gap
           Print values to Serial Monitor
       (repeat the melody from the beginning)

#. **Library Include, Melody Array, and Constants**

   - ``MELODY[]`` stores four note frequencies — C4 (262 Hz), E4 (330 Hz), G4 (392 Hz), C5 (523 Hz) — in an array, just like the LED pin arrays you used earlier
   - ``MELODY_LENGTH`` is calculated automatically from the array size — add more notes and it updates without changing any other code
   - ``MIN_PITCH_PERCENT`` and ``MAX_PITCH_PERCENT`` define how far the potentiometer can shift the pitch: 50% (one octave lower) to 200% (one octave higher)

   .. code-block:: arduino

      const uint16_t MELODY[] = {262, 330, 392, 523};
      const int MELODY_LENGTH = sizeof(MELODY) / sizeof(MELODY[0]);
      const int MIN_PITCH_PERCENT = 50;
      const int MAX_PITCH_PERCENT = 200;

#. **Reading the Potentiometer and Mapping to Pitch**

   - ``analogRead()`` returns 0–1023 from pin A2; ``map()`` rescales to 50–200%
   - Each note's base frequency is multiplied by this percentage — ``MELODY[note] * pitchPercent / 100``
   - At minimum (50%), the melody plays an octave lower; at maximum (200%), an octave higher. The ratios between notes stay the same, so the melody is always recognizable.

   .. code-block:: arduino

      int potValue = analogRead(POT_PIN);
      int pitchPercent = map(potValue, 0, 1023, 50, 200);
      uint16_t frequency = (uint32_t)MELODY[note] * pitchPercent / 100;

#. **Playing and Stopping a Note**

   - ``playFrequency()`` calculates the PWM period (microseconds per cycle) and pulse (half the period for 50% duty cycle), then sets the frequency and enables the output
   - ``stopBuzzer()`` disables the output between notes, creating a short gap so they don't blur together
   - The ``for`` loop in ``loop()`` plays each note in sequence, then repeats from the beginning

   .. code-block:: arduino

      void playFrequency(uint16_t frequency) {
          uint32_t period = 1000000UL / frequency;
          uint16_t pulse = period / 2;
          buzzer.setFreq(frequency);
          buzzer.setPulse(pulse);
          buzzer.setEnable(true);
      }

**Passive Buzzer vs Active Buzzer**

You've used both types now — let's compare them:

  * **Active buzzer** (Tilt Alarm): Has a built-in oscillator. Apply DC voltage → it beeps at a fixed frequency. Simple on/off control. Good for alarms and alerts.
  * **Passive buzzer** (this lesson): No internal oscillator. You supply a square wave (AC signal) via PWM. You control both the frequency (pitch) and the duty cycle (volume/timbre). Good for music, sound effects, and variable tones.

  **With an active buzzer you say "beep or don't beep." With a passive buzzer you say "play this exact note."**

**Two Ways to Drive a Passive Buzzer**

In the PIR Motion Alarm lesson, you drove a passive buzzer on pin **D5** with ``tone(buzzerPin, 800)`` — one line of code, no library. This lesson uses a different approach: the buzzer connects to **P5** on the Robot Shield and is driven by the ``Pwm`` class from the RobotShield library. Both methods work — so why the change?

  * **``tone()`` on a digital pin** — Arduino generates the square wave in **software** on the main MCU. Simple and direct, perfect when you just need a beep or a siren.

  * **``Pwm`` on the Robot Shield** — the Robot Shield's own chip generates the wave in **hardware** (I2C carries only the frequency and pulse settings). The main MCU stays free to read sensors, do math, and run other code.

  * **This lesson's goal is the math** — ``setFreq()`` and ``setPulse()`` make the frequency → period → duty cycle relationship **explicit**. ``tone()`` hides all of that behind one function call, so you'd never see the ``1000000 / frequency`` conversion that connects pitch to microseconds. Seeing it here prepares you for PWM control of motors, servos, and LEDs, where the same period/pulse concepts apply.

3. Experiment
----------------

**Change the Melody**

Try replacing the ``MELODY`` array with different notes:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Notes
     - Frequencies
   * - ``{262, 294, 330, 349, 392, 440, 494, 523}``
     - C major scale — eight ascending notes
   * - ``{523, 392, 330, 262}``
     - Reversed — melody plays highest note first

**Adjust the Pitch Range**

Change ``MIN_PITCH_PERCENT`` and ``MAX_PITCH_PERCENT`` to control how far the knob shifts the pitch:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Range
     - Effect
   * - 80 to 120
     - Subtle — knob only slightly bends the pitch
   * - 50 to 200
     - Default — one octave down to one octave up
   * - 25 to 400
     - Extreme — very low rumble to piercing high notes


4. Troubleshooting
--------------------

**Buzzer makes no sound at all**

* **Cause:** The buzzer is not connected properly, or the PWM channel is not enabled.
* **Solution:** Check that the buzzer's two pins are firmly seated in the breadboard — one connected to pin P5, the other to GND. A passive buzzer has no polarity, so either pin can go to either rail. Make sure the code calls ``buzzer.setEnable(true)``.

**Melody pitch does not change when turning the knob**

* **Cause:** The potentiometer is wired incorrectly, or the code is reading the wrong pin.
* **Solution:** Verify the middle pin of the potentiometer connects to A2. The outer pins should connect to 3.3V and GND. Open the Serial Monitor — if the potentiometer value stays at 0 or 1023 regardless of knob position, the wiring is likely wrong.

**Knob works backwards (clockwise lowers the pitch)**

* **Cause:** The outer pins of the potentiometer are swapped (3.3V and GND reversed).
* **Solution:** Swap the connections to the two outer pins of the potentiometer. Alternatively, use ``map(potValue, 0, 1023, 200, 50)`` to reverse the behavior in code.

**Buzzer sounds weak or distorted**

* **Cause:** The duty cycle is not set to 50%.
* **Solution:** Make sure ``pulse = period / 2`` — this creates a 50% duty cycle, which gives the strongest and cleanest tone.

**Serial Monitor shows correct frequency but no sound**

* **Cause:** The buzzer might be an active buzzer (with internal oscillator) instead of a passive one.
* **Solution:** Active buzzers ignore PWM frequency changes — they only beep at their fixed internal frequency. Check that your buzzer is a **passive** type (usually has a bare metal disc visible on top, without a sealed plastic cap).

5. Summary
-------------

Congratulations! You've made music — not just a single tone, but a melody that you can control with a knob. In this lesson, you learned:

* How to store a melody in an **array** and play notes in sequence with a ``for`` loop (building on earlier array lessons)
* How ``map()`` converts a potentiometer reading into a pitch percentage that shifts the entire melody
* How PWM generates audio frequencies via the Robot Shield — the same technology behind dimmable LEDs
* The relationship between **frequency** (pitch in Hz), **period** (microseconds per cycle), and **duty cycle**
* The difference between active buzzers and passive buzzers

The combination of arrays, analog input, and PWM opens up a world of possibilities — from musical instruments to audio feedback. In the next lesson, you'll use an ultrasonic sensor to measure distance with sound waves — building a proximity alarm that beeps faster as obstacles get closer.
