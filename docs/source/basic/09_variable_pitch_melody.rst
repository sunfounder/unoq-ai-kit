.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

09 Variable Pitch Melody
========================

Earlier, you used a photoresistor to read light levels — your first analog sensor. Now you'll use a **potentiometer** to control a passive buzzer — not just a single tone, but a repeating four-note melody. Turn the knob one way and the entire melody shifts higher; turn it the other way and it drops lower. The musical intervals stay intact — the tune is recognizable at any pitch.

In this lesson, you will learn to:

* Apply ``analogRead()`` with a new sensor — the potentiometer
* Control a passive buzzer's **frequency** with ``tone()``
* Use the ``map()`` function to convert potentiometer readings into a pitch percentage
* Store a melody in an **array** and play notes in sequence
* Calculate note **frequencies** from a melody array and a pitch percentage

1. Setup
----------------------

**What You Need**

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

**Software Requirements**

This project uses no external libraries — the sketch only uses the built-in Arduino framework.

**Wiring Diagram**

Connect the passive buzzer — it has **no polarity**, so either orientation works — to **D5**, and the potentiometer's **left pin to 3.3V**, **middle (wiper) pin to A2**, and **right pin to GND**; reversing 3.3V and GND won't damage the potentiometer, but the knob will behave backwards (clockwise lowers the pitch instead of raising it). Unlike an **active buzzer**, which buzzes by itself the moment it is powered, a **passive buzzer** makes no sound on its own — the sketch must generate the sound wave with ``tone()``.

.. image:: /img/wiring/wiring_pot_buzzer.png
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

#. Navigate to the ``unoq-ai-kit/basic/`` folder and select ``09 Variable Pitch Melody.zip``. The app appears in **Apps** — click it to open.

#. With the app open, click the **Run** button (▶) in the top-right corner.

   .. image:: /img/app_run.png
      :width: 500

#. Wait a few seconds for the upload to finish, then open the **Serial Monitor** (📊 icon in the top bar). You should hear a repeating four-note melody. Turn the potentiometer — the entire melody shifts higher or lower while keeping the same tune. Open the Serial Monitor to see the current frequency.

**The Sketch (sketch.ino)**

Now that you've heard the melody change pitch, let's look at the sketch file.

.. code-block:: cpp
   :linenos:

   /*
    * Variable Pitch Melody
    *
    * Turn the potentiometer to raise or lower the pitch of the whole melody.
    *
    * Potentiometer: A2
    * Passive buzzer: D5 (driven with tone())
    */

   const int POT_PIN = A2;
   const int BUZZER_PIN = 5;

   const int MIN_PITCH_PERCENT = 50;
   const int MAX_PITCH_PERCENT = 200;

   const int NOTE_DURATION = 250;
   const int NOTE_GAP = 50;

   const uint16_t MELODY[] = {
       262,  // C4
       330,  // E4
       392,  // G4
       523   // C5
   };

   const int MELODY_LENGTH = sizeof(MELODY) / sizeof(MELODY[0]);

   void playFrequency(uint16_t frequency)
   {
       tone(BUZZER_PIN, frequency);
   }

   void stopBuzzer()
   {
       noTone(BUZZER_PIN);
   }

   void setup()
   {
       Serial.begin(115200);

       pinMode(BUZZER_PIN, OUTPUT);
       noTone(BUZZER_PIN);

       Serial.println("=== Variable Pitch Melody ===");
       Serial.println("Turn the potentiometer to change the melody pitch.");
   }

   void loop()
   {
       for (int note = 0; note < MELODY_LENGTH; note++)
       {
           int potValue = analogRead(POT_PIN);

           int pitchPercent = map(
               potValue,
               0,
               1023,
               MIN_PITCH_PERCENT,
               MAX_PITCH_PERCENT
           );

           uint16_t frequency =
               (uint32_t)MELODY[note] * pitchPercent / 100;

           playFrequency(frequency);

           Serial.print("Potentiometer: ");
           Serial.print(potValue);
           Serial.print("    Pitch: ");
           Serial.print(pitchPercent);
           Serial.print("%    Note frequency: ");
           Serial.print(frequency);
           Serial.println(" Hz");

           delay(NOTE_DURATION);

           stopBuzzer();
           delay(NOTE_GAP);
       }
   }

**How it Works**

This lesson introduces three new ideas — a melody stored in an array, pitch control via the potentiometer, and frequency generation with ``tone()`` — working together:

.. code-block:: text

   setup() → runs once at startup:
       Start Serial Monitor
       Set buzzer pin D5 as an output, start it silent
       Print startup message

   loop() → runs over and over forever:
       For each note in the melody:
           Read potentiometer on A2 (0–1023)
           Map to pitch percentage (50–200%)
           Multiply note frequency by pitch percentage
           Play the note for 250ms with tone()
           Silence for 50ms gap with noTone()
           Print values to Serial Monitor
       (repeat the melody from the beginning)

#. **Constants, Melody Array, and Pins**

   - ``POT_PIN`` (A2) and ``BUZZER_PIN`` (D5) name the pins — the buzzer connects straight to a digital pin, no extra hardware needed
   - ``MELODY[]`` stores four note frequencies — C4 (262 Hz), E4 (330 Hz), G4 (392 Hz), C5 (523 Hz) — in an array, just like the LED pin arrays you used earlier
   - ``MELODY_LENGTH`` is calculated automatically from the array size — add more notes and it updates without changing any other code
   - ``MIN_PITCH_PERCENT`` and ``MAX_PITCH_PERCENT`` define how far the potentiometer can shift the pitch: 50% (one octave lower) to 200% (one octave higher)

   .. code-block:: arduino

      const int POT_PIN = A2;
      const int BUZZER_PIN = 5;
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
      int pitchPercent = map(potValue, 0, 1023,
                             MIN_PITCH_PERCENT, MAX_PITCH_PERCENT);
      uint16_t frequency = (uint32_t)MELODY[note] * pitchPercent / 100;

#. **Playing and Stopping a Note**

   - ``playFrequency()`` calls ``tone(BUZZER_PIN, frequency)`` — one line of code makes the buzzer produce a square wave at the requested frequency, which you hear as a pitch
   - ``stopBuzzer()`` calls ``noTone(BUZZER_PIN)`` to silence the buzzer between notes, creating a short gap so they don't blur together
   - The ``for`` loop in ``loop()`` plays each note in sequence, then repeats from the beginning

   .. code-block:: arduino

      void playFrequency(uint16_t frequency) {
          tone(BUZZER_PIN, frequency);
      }

      void stopBuzzer() {
          noTone(BUZZER_PIN);
      }

**Passive Buzzer vs Active Buzzer**

You've used both types now — let's compare them:

  * **Active buzzer** (Tilt Alarm): Has a built-in oscillator. Apply DC voltage → it beeps at a fixed frequency. Simple on/off control. Good for alarms and alerts.
  * **Passive buzzer** (this lesson): No internal oscillator. You supply a square wave (AC signal) with ``tone()``. You control the frequency (pitch) by choosing the frequency you pass in. Good for music, sound effects, and variable tones.

  **With an active buzzer you say "beep or don't beep." With a passive buzzer you say "play this exact note."**

**tone() with a Frequency You Compute**

In the PIR Motion Alarm lesson, you drove a passive buzzer on pin **D5**, alternating between ``tone(buzzerPin, 800)`` and ``tone(buzzerPin, 1200)`` — a two-tone siren. This lesson uses the same function and the same pin, but now the frequency changes with every note:

  * **``tone(BUZZER_PIN, frequency)``** — Arduino generates the square wave in **software** on the main MCU: it toggles pin D5 at the frequency you pass in. One line of code, no library, no extra hardware.

  * **The frequency comes from your code** — ``MELODY[note] * pitchPercent / 100`` combines the melody array with the knob position. That math is the real goal of this lesson: turning data into sound, not driving the buzzer.

  * **``noTone(BUZZER_PIN)``** — stops the wave so you can insert the 50ms silence between notes, keeping them separate.

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

* **Cause:** The buzzer is not connected properly, or the buzzer pin is not set as an output.
* **Solution:** Check that the buzzer's two pins are firmly seated in the breadboard — one connected to pin D5, the other to GND. A passive buzzer has no polarity, so either pin can go to either rail. Make sure ``setup()`` calls ``pinMode(BUZZER_PIN, OUTPUT)``.

**Melody pitch does not change when turning the knob**

* **Cause:** The potentiometer is wired incorrectly, or the code is reading the wrong pin.
* **Solution:** Verify the middle pin of the potentiometer connects to A2. The outer pins should connect to 3.3V and GND. Open the Serial Monitor — if the potentiometer value stays at 0 or 1023 regardless of knob position, the wiring is likely wrong.

**Knob works backwards (clockwise lowers the pitch)**

* **Cause:** The outer pins of the potentiometer are swapped (3.3V and GND reversed).
* **Solution:** Swap the connections to the two outer pins of the potentiometer. Alternatively, use ``map(potValue, 0, 1023, 200, 50)`` to reverse the behavior in code.

**Buzzer sounds weak or distorted**

* **Cause:** The knob is at the minimum pitch — the lowest notes (around 131 Hz) sound weak and buzzy on a small buzzer.
* **Solution:** Turn the knob toward the middle or upper range. If the sound is still weak at high pitches, reseat the buzzer's pins in the breadboard — a loose connection can muffle the tone.

**Serial Monitor shows correct frequency but no sound**

* **Cause:** The buzzer might be an active buzzer (with internal oscillator) instead of a passive one.
* **Solution:** Active buzzers ignore frequency changes — they only beep at their fixed internal frequency. Check that your buzzer is a **passive** type (usually has a bare metal disc visible on top, without a sealed plastic cap).

5. Summary
-------------

Congratulations! You've made music — not just a single tone, but a melody that you can control with a knob. In this lesson, you learned:

* How to store a melody in an **array** and play notes in sequence with a ``for`` loop (building on earlier array lessons)
* How ``map()`` converts a potentiometer reading into a pitch percentage that shifts the entire melody
* How ``tone()`` generates audio frequencies — a square wave on a digital pin whose frequency sets the pitch
* How the **frequency** (pitch in Hz) of each note is calculated from the melody array and the knob's pitch percentage
* The difference between active buzzers and passive buzzers

The combination of arrays, analog input, and PWM opens up a world of possibilities — from musical instruments to audio feedback. In the next lesson, you'll use an ultrasonic sensor to measure distance with sound waves — building a proximity alarm that beeps faster as obstacles get closer.
