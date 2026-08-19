.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

2. AI Voice Wake-Up
=======================

In the previous lesson, your UNO Q learned to see. Now it will learn to **hear**. You'll build a voice wake-up system that listens for the phrase "Hello Arduino" and responds with a buzzer — just like how "Hey Siri" or "OK Google" wake up your phone.

In this lesson, you will learn to:

* Capture audio from the onboard microphone
* Run a keyword spotting model on the UNO Q
* Trigger a hardware output (buzzer) when the keyword is detected
* Understand the audio AI pipeline: mic → spectrogram → model → action

1. Setup
----------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * :ref:`Arduino Uno Q <cpn_uno_q>`
     - 1 * Multimedia Carrier
     - 1 * :ref:`cpn_buzzer`
     - Several :ref:`cpn_wires`
   * - |list_uno_q|
     - |list_uno_q|
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

.. note::

   The Multimedia Carrier has a built-in microphone — no external mic needed. The buzzer provides simple feedback; you could also use the onboard LEDs.

**Hardware Setup**

#. Connect the active buzzer: **VCC** → **digital pin 5**, **GND** → any **GND** pin.

#. Make sure the Multimedia Carrier is attached to the UNO Q. The onboard microphone faces forward — speak toward the Carrier, not the breadboard.

.. image:: img/2_voice_wakeup_setup.png
   :width: 600
   :align: center

2. Code
----------

**Import the Code**

#. Open **Arduino App Lab**, go to **Apps**. Click **Import App**, then **Import from Computer**.

#. Navigate to ``unoq-ai-kit/edge_ai/`` and select ``2_ai_voice_wakeup.zip``.

#. Open the imported app.

**Run the Code**

#. Click the **Run** button (▶). Wait for the model to load.

#. Say "**Hello Arduino**" clearly toward the Multimedia Carrier. The buzzer should beep once for each detection.

#. Try saying other phrases ("hello computer", "hi there", random noise). The buzzer should remain silent — the model only responds to its trained keyword.

**The Code**

.. code-block:: cpp
   :linenos:

   /*
    * Lesson 2: AI Voice Wake-Up
    * Detects the keyword "Hello Arduino" and triggers a buzzer.
    */

   #include <Arduino_RouterBridge.h>
   #include "microphone.h"
   #include "edge_impulse.h"

   const int buzzerPin = 5;

   void setup() {
       Monitor.begin();
       pinMode(buzzerPin, OUTPUT);

       Microphone.begin();              // Initialize the microphone
       AI.begin("keyword_spotting.eim"); // Load the keyword model
   }

   void loop() {
       // Capture a 1-second audio sample
       Microphone.capture(1000);

       // Run inference on the audio sample
       AIResult result = AI.classify();

       // Check if the wake word was detected
       if (result.label == "hello_arduino" && result.confidence > 0.7) {
           Monitor.println("Wake word detected!");

           // Beep the buzzer as confirmation
           digitalWrite(buzzerPin, HIGH);
           delay(200);
           digitalWrite(buzzerPin, LOW);
       }

       // Print confidence scores to Monitor
       Monitor.print("hello_arduino: ");
       Monitor.print(result.confidence * 100);
       Monitor.println("%");
   }

**How it Works**

.. code-block:: text

   setup() → runs once:
       Initialize microphone hardware
       Load keyword spotting model

   loop() → runs forever:
       Record 1 second of audio
       Convert audio to spectrogram (frequency image)
       Run AI model on spectrogram
       Is "hello_arduino" detected with >70% confidence?
           YES → beep buzzer
           NO  → do nothing

Here's what's happening under the hood:

* **Audio capture** — The microphone records raw sound waves as a stream of amplitude values (44,100 samples per second at 16-bit resolution).
* **Spectrogram conversion** — Raw audio is converted into a spectrogram — a 2D image where the X-axis is time, the Y-axis is frequency, and pixel brightness represents energy. The AI model "sees" sound as images.
* **Keyword spotting model** — A neural network trained on thousands of audio clips of people saying "Hello Arduino" (and thousands of clips of other words and background noise). It classifies each 1-second window as either containing the keyword or not.
* **Confidence threshold (0.7)** — The model outputs a probability between 0 and 1. We only trigger the buzzer above 0.7 (70%) to avoid false activations from similar-sounding words or noise.

3. Experiment
----------------

**Adjust the Sensitivity**

Change the confidence threshold and observe how it affects behavior:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Threshold
     - Behavior
   * - ``0.5``
     - More sensitive — may false-trigger on similar words
   * - ``0.7`` (default)
     - Balanced — reliable detection, few false triggers
   * - ``0.9``
     - Strict — only triggers with very clear pronunciation

**Challenge: Custom Response Pattern**

Instead of a single 200ms beep, make the buzzer play a short melody when the wake word is detected. Try three ascending beeps (100ms, 150ms, 200ms) with 50ms gaps.

**Challenge: Background Noise Test**

Run the model while playing music or with a fan running nearby. How does background noise affect the confidence scores? Keyword spotting models are trained with background noise augmentation, so they should still work — but watch how the scores change.

4. Troubleshooting
--------------------

**Buzzer never triggers, even when saying "Hello Arduino" clearly**

* **Cause:** Speaking too far from the microphone, or pronunciation differs from the training data.
* **Solution:** Speak within 30 cm of the Multimedia Carrier, facing the microphone. Pronounce each word clearly: "Hel-lo Ar-dui-no". Check the Monitor to see your actual confidence scores.

**Buzzer triggers randomly when nobody is speaking**

* **Cause:** Confidence threshold is too low, or there's loud background noise.
* **Solution:** Increase the threshold from ``0.7`` to ``0.8`` or ``0.85``. Move away from fans, air conditioners, or other noise sources.

**"Failed to load model" or "Microphone not found"**

* **Cause:** The Multimedia Carrier is not properly attached, or the .eim file is missing.
* **Solution:** Reseat the Multimedia Carrier on the bottom connector. Make sure ``keyword_spotting.eim`` is included in the app's assets.

**Model recognizes the keyword but takes too long to respond**

* **Cause:** Audio capture + inference happens in a blocking loop; the response feels delayed.
* **Solution:** The 1-second capture window plus inference time (~100–300ms) means total latency is about 1.3 seconds. This is normal for edge AI keyword spotting.

5. Summary
-------------

Your UNO Q can now hear you! In this lesson, you learned:

* How the onboard microphone captures audio for AI processing
* How a keyword spotting model converts sound into spectrograms and classifies them
* How confidence thresholds balance sensitivity against false triggers
* How to use AI output to control a physical component (buzzer)

In the next lesson, you'll combine vision with motion — using the pan-tilt to track a person's face as they move.
