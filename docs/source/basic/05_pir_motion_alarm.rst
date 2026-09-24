.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

05 PIR Motion Alarm
======================

You've used buttons, tilt switches, and photoresistors to detect physical states. Now you'll use a sensor that can detect **people** — the PIR (Passive Infrared) motion sensor. When it spots movement, a passive buzzer sounds a two-tone warning siren — just like the motion-activated lights and security systems in everyday life.

In this lesson, you will learn to:

* Read a PIR motion sensor — a digital sensor that detects infrared heat changes
* Control a passive buzzer with ``tone()`` and ``noTone()`` to generate specific frequencies
* Create a two-tone siren effect by alternating between two frequencies
* Understand why PIR sensors need a warm-up period before they work reliably

1. Setup
----------------------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_pir`
     - 1 * Passive :ref:`cpn_buzzer`
     - Several :ref:`cpn_wires`
   * - |list_pan_tilt|
     - |list_pir|
     - |list_passive_buzzer|
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

Connect the PIR sensor's three pins — **VCC → 5V**, **GND → GND**, **OUT → D4** — and the passive buzzer to **D5**.

.. image:: /img/wiring/wiring_pc_buzzer_pir.png
   :width: 600
   :align: center

2. Run the App
----------------

**Import and Run the Code**

#. Download :download:`05 PIR Motion Alarm.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/05.PIR.Motion.Alarm.zip>`.
#. In App Lab, go to **Apps** → **Create new app** → **Import App** → **Import from Computer**, and open the package you downloaded.
#. Click the **Run** button (▶) in the top-right corner.

   .. image:: /img/app_run.png
      :width: 500

#. The Serial Monitor opens. The PIR sensor needs **30 seconds** to warm up — you'll see "PIR Motion Alarm — warming up (30 seconds)..." followed by "Ready!" Once ready, wave your hand or walk in front of the sensor. The buzzer sounds a two-tone siren — alternating 800 Hz and 1200 Hz.

**The Sketch (sketch.ino)**

Now that you've seen the alarm in action, let's look at the sketch.

.. code-block:: cpp
   :linenos:

   const int pirPin = 4;     // PIR sensor OUT connected to D4
   const int buzzerPin = 5;  // Passive buzzer connected to D5

   void setup() {
       pinMode(pirPin, INPUT);
       pinMode(buzzerPin, OUTPUT);
       noTone(buzzerPin);

       Serial.begin(115200);
       Serial.println("PIR Motion Alarm — warming up (30 seconds)...");
       delay(30000);  // PIR sensor warm-up period
       Serial.println("Ready! Move in front of the sensor.");
   }

   void loop() {
       int motion = digitalRead(pirPin);

       if (motion == HIGH) {
           Serial.println("Motion detected!");

           // Alternate between two tones to create a warning sound
           tone(buzzerPin, 800);
           delay(250);

           tone(buzzerPin, 1200);
           delay(250);

           tone(buzzerPin, 800);
           delay(250);

           tone(buzzerPin, 1200);
           delay(250);

           noTone(buzzerPin);

           delay(500);  // Pause before checking again
       } else {
           noTone(buzzerPin);  // No motion → silent
       }
   }

**How it Works**

This lesson combines a PIR sensor with a passive buzzer — you've used active buzzers before (just on/off with ``digitalWrite()``), but a passive buzzer gives you control over the actual **sound** by setting the frequency:

.. code-block:: text

   setup() → runs once at startup:
       Configure PIR pin as INPUT, buzzer pin as OUTPUT
       Call noTone() to ensure buzzer starts silent
       Start Serial Monitor
       Wait 30 seconds for PIR sensor to stabilize (warm-up)

   loop() → runs over and over forever:
       Read PIR sensor (digitalRead)
       If HIGH (motion detected):
           Print "Motion detected!" to Serial Monitor
           tone(800 Hz)  → delay(250)
           tone(1200 Hz) → delay(250)
           tone(800 Hz)  → delay(250)
           tone(1200 Hz) → delay(250)
           noTone() — stop the sound
           Pause 500 ms
       Else (no motion):
           noTone() — keep buzzer silent

#. **Pin Configuration and noTone()**

   - The PIR pin is configured as a standard digital ``INPUT``, and the buzzer pin as ``OUTPUT`` — no library needed
   - ``noTone(buzzerPin)`` in ``setup()`` makes sure the buzzer starts silent — it stops any tone signal that might be on the pin from a previous run
   - ``noTone()`` is also called in the ``else`` branch of ``loop()`` to keep the buzzer off when there's no motion

   .. code-block:: arduino

      const int pirPin = 4;
      const int buzzerPin = 5;

      pinMode(pirPin, INPUT);
      pinMode(buzzerPin, OUTPUT);
      noTone(buzzerPin);

#. **How tone() Works**

   - ``tone(pin, frequency)`` generates a 50% duty-cycle square wave at the specified pin and frequency — the passive buzzer vibrates at that frequency to produce audible sound
   - You call ``tone()`` with a new frequency, and it immediately changes the pitch — no need to call ``noTone()`` between notes
   - ``tone()`` runs in the background — once called, the square wave keeps going while your code does other things (like ``delay()``)
   - Here, ``tone(buzzerPin, 800)`` plays 800 Hz and ``tone(buzzerPin, 1200)`` plays 1200 Hz — alternating them creates a siren effect

   .. code-block:: arduino

      tone(buzzerPin, 800);
      delay(250);

      tone(buzzerPin, 1200);
      delay(250);

#. **The 30-Second Warm-Up**

   - When a PIR sensor is first powered on, it needs time to measure the background infrared level of the room
   - During warm-up the output may trigger randomly — the ``delay(30000)`` ignores this unstable period
   - Warm-up happens once per power-up, not every loop — that's why it lives in ``setup()``, not ``loop()``
   - The Serial Monitor prints a message so you know the sensor isn't broken — it's just calibrating

   .. code-block:: arduino

      Serial.println("PIR Motion Alarm — warming up (30 seconds)...");
      delay(30000);
      Serial.println("Ready! Move in front of the sensor.");

#. **The Two-Tone Siren Pattern**

   - Alternating between 800 Hz and 1200 Hz creates a classic warning siren — the frequency change grabs attention better than a single steady tone
   - Each ``tone()`` is followed by ``delay(250)``, so each pitch plays for 250 ms before switching
   - After all four tones, ``noTone(buzzerPin)`` stops the sound, and ``delay(500)`` creates a gap before the siren can retrigger — this prevents a single motion event from looping the siren endlessly

   .. code-block:: arduino

      tone(buzzerPin, 800);
      delay(250);

      tone(buzzerPin, 1200);
      delay(250);

      tone(buzzerPin, 800);
      delay(250);

      tone(buzzerPin, 1200);
      delay(250);

      noTone(buzzerPin);

      delay(500);

**Passive Buzzer vs Active Buzzer**

You've used both types now — let's compare them:

  * **Active buzzer** (Tilt Alarm): Has a built-in oscillator. Apply DC voltage → it beeps at a fixed frequency. Simple on/off control with ``digitalWrite()``. Good for alarms and alerts where the exact pitch doesn't matter.

  * **Passive buzzer** (this lesson): No internal oscillator. You supply a square wave — Arduino's ``tone()`` generates it at the desired frequency. You control both the pitch (frequency in Hz) and the duration. Good for sirens, melodies, and sound effects.

  **With an active buzzer you say "beep or don't beep." With a passive buzzer you say "play this exact note for this long."**

3. Experiment
----------------

**Change the Siren Frequencies**

The two-tone siren alternates between 800 Hz and 1200 Hz — try different frequency pairs to create your own alarm sound:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Frequencies
     - Effect
   * - 500 Hz / 1000 Hz
     - Lower, slower siren — sounds like a European police car
   * - 1000 Hz / 1500 Hz
     - Higher, more urgent — sounds like a smoke detector
   * - 400 Hz / 400 Hz
     - Same frequency twice — single steady tone, no siren effect
   * - 200 Hz / 3000 Hz
     - Extreme range — sounds like a sci-fi alarm

**Challenge: Motion Counter**

Add a counter variable that increments each time motion is detected. Print the count to the Serial Monitor. How many times did someone walk past your sensor in one minute?

.. dropdown:: Click to reveal solution
   :open:

   Add before ``setup()``:

   .. code-block:: cpp

      int motionCount = 0;

   Add inside the ``if (motion == HIGH)`` block, after ``Serial.println("Motion detected!")``:

   .. code-block:: cpp

      motionCount++;
      Serial.print("Motion count: ");
      Serial.println(motionCount);

4. Troubleshooting
--------------------

**"Buzzer beeps constantly even when nothing is moving"**

* **Cause:** The PIR sensor is still in its warm-up phase, or there is a source of heat or wind near the sensor.
* **Solution:** Wait a full 30 seconds after power-up. Keep the sensor away from sunny windows, air conditioning vents, and heat sources — these can trigger false detections.

**"No alarm when I move in front of the sensor"**

* **Cause:** The PIR sensor's detection range or delay potentiometer is set incorrectly.
* **Solution:** Look for the two orange adjustment potentiometers on the PIR module. Turn the distance adjustment clockwise to increase range (up to 7 m). Turn the delay adjustment counterclockwise to reduce the hold time (minimum ~5 s). Also check that the jumper cap is set to **H** (repeatable trigger mode).

**"Alarm only triggers once, then never again"**

* **Cause:** The PIR module's jumper cap is set to **L** (non-repeatable trigger mode).
* **Solution:** Move the jumper cap on the PIR module from the L position to the H position. H mode keeps the OUT pin HIGH as long as motion continues; L mode only triggers once per motion event.

**"Serial Monitor shows 'Motion detected!' but the buzzer doesn't sound"**

* **Cause:** The passive buzzer is not connected to D5, or the buzzer is faulty.
* **Solution:** Verify the passive buzzer is connected between D5 and GND. Unlike an active buzzer, a passive buzzer has **no polarity** — either lead can go to D5 or GND. Try swapping the leads to rule out a loose connection.

**"Buzzer makes a faint, distorted, or clicking sound instead of a clean tone"**

* **Cause:** The buzzer pin may not support ``tone()`` on this board, or the connections are loose.
* **Solution:** Check that the passive buzzer's leads are firmly inserted into the breadboard. Verify the buzzer is on pin D5 — if the pin was accidentally changed in code, update ``buzzerPin`` to match the physical connection. If the sound is still weak, try a different digital pin (D2, D3, or D6) and update the code accordingly.

5. Summary
-------------

You've built a motion-activated alarm with a two-tone siren — the same principle behind automatic lights, security systems, and wildlife cameras. In this lesson, you learned:

* How a PIR sensor detects motion by sensing changes in infrared radiation
* Why PIR sensors need a 30-second warm-up to calibrate to the background environment
* How ``tone()`` generates a square wave at a specific frequency to drive a passive buzzer
* The difference between active buzzers (simple on/off with ``digitalWrite()``) and passive buzzers (frequency control with ``tone()``)

You've come a long way — from blinking a single LED to building a motion-detecting alarm system. You understand digital output and input, the tilt switch, analog input, and now infrared motion detection. Everything you've learned here is a foundation for the IoT, AI, and multimedia projects ahead.
