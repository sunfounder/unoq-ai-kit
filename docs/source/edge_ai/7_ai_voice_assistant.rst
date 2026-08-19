.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

7. AI Voice Assistant
=========================

In the previous lesson, your UNO Q followed one-way voice commands. Now you'll build a **two-way conversation**: you ask a question, and the device **speaks back** to you. Using Speech-to-Text (STT) to understand you and Text-to-Speech (TTS) to respond, you'll create a simple AI assistant that can answer questions and confirm your commands.

In this lesson, you will learn to:

* Use Speech-to-Text to convert spoken words into text
* Use Text-to-Speech to synthesize spoken responses
* Build a conversational loop: listen → process → speak
* Combine voice input with vision output ("What do you see?")

1. Setup
----------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * :ref:`Arduino Uno Q <cpn_uno_q>`
     - 1 * Multimedia Carrier
     - 1 * Camera Module
     - 1 * :ref:`cpn_servo`
   * - |list_uno_q|
     - |list_uno_q|
     - |list_uno_q|
     - |list_servo|
   * - Several :ref:`cpn_wires`
     - 1 * USB Cable
     -
     -
   * - |list_wire|
     - |list_usb_cable|
     -
     -

.. note::

   The Multimedia Carrier includes a speaker (4Ω/3W) for audio output. Make sure nothing is blocking the speaker grille. The onboard microphone handles input.

**Hardware Setup**

#. Connect the servo: signal to **digital pin 9**, power to **5V**, ground to **GND**.
#. The camera, microphone, and speaker are all built into the Multimedia Carrier — no additional wiring needed.

.. image:: img/7_assistant_setup.png
   :width: 600
   :align: center

2. Code
----------

**Import the Code**

#. In App Lab, go to **Apps** → **Import App** → **Import from Computer**.

#. Navigate to ``unoq-ai-kit/edge_ai/`` and select ``7_ai_voice_assistant.zip``.

#. Open the imported app.

**Run the Code**

#. Click the **Run** button (▶).

#. Say "**What do you see?**" — the camera captures an image, runs object detection, and the speaker responds: "I see a person" or "I see a cup".

#. Say "**Turn left**" — the servo rotates left, and the speaker confirms: "Turning left".

#. Say "**Hello**" — the speaker responds with a greeting.

.. image:: img/7_assistant_result.gif
   :width: 600
   :align: center

**The Code**

.. code-block:: cpp
   :linenos:

   /*
    * Lesson 7: AI Voice Assistant
    * Speech-to-text input, text-to-speech output.
    */

   #include <Arduino_RouterBridge.h>
   #include <Servo.h>
   #include "microphone.h"
   #include "speaker.h"
   #include "camera.h"
   #include "edge_impulse.h"

   Servo myServo;
   const int servoPin = 9;

   void setup() {
       Monitor.begin();
       Microphone.begin();
       Speaker.begin();  // Initialize the speaker
       Camera.begin();
       AI.begin("voice_assistant.eim");

       myServo.attach(servoPin);
       myServo.write(90);

       // Greet the user on startup
       Speaker.say("Hello, I am ready. Ask me what I see, or tell me to turn.");
   }

   void processCommand(String command) {
       Monitor.print("Heard: ");
       Monitor.println(command);

       if (command == "what_do_you_see") {
           // Capture image and run object detection
           Camera.capture();
           AI.begin("object_detection.eim");
           AIResult vision = AI.classify();
           AI.begin("voice_assistant.eim");  // Switch back to voice model

           if (vision.detected && vision.confidence > 0.6) {
               String response = "I see a " + vision.label;
               Speaker.say(response);
           } else {
               Speaker.say("I don't see anything clearly.");
           }
       }
       else if (command == "turn_left") {
           myServo.write(45);
           Speaker.say("Turning left.");
       }
       else if (command == "turn_right") {
           myServo.write(135);
           Speaker.say("Turning right.");
       }
       else if (command == "look_center") {
           myServo.write(90);
           Speaker.say("Looking center.");
       }
       else if (command == "hello") {
           Speaker.say("Hello! How can I help you?");
       }
       else {
           Speaker.say("I didn't understand that command.");
       }
   }

   void loop() {
       Microphone.capture(2000);  // Listen for 2 seconds
       AIResult result = AI.classify();

       if (result.detected && result.confidence > 0.65) {
           processCommand(result.label);
       }
   }

**How it Works**

.. code-block:: text

   setup() → runs once:
       Initialize mic, speaker, camera, AI model
       Centered servo
       Greet the user with TTS

   loop() → runs forever:
       Record 2s of audio → STT converts speech to text
       Command detected?
           YES → processCommand():
               "what_do_you_see" → capture image → object detection → TTS response
               "turn_left/right"  → move servo → TTS confirmation
               "hello"            → TTS greeting
               unknown            → TTS error message
           NO  → listen again

Here's what's new in this lesson:

* **Text-to-Speech (TTS)** — ``Speaker.say("Hello")`` converts text into spoken audio and plays it through the Multimedia Carrier's speaker. The TTS engine runs locally on the UNO Q — no internet connection needed.
* **Model switching** — The ``processCommand()`` temporarily switches to the object detection model (``AI.begin("object_detection.eim")``) for the "what do you see" query, then switches back to the voice model. This demonstrates multi-model applications: different AI models for different tasks.
* **Conversational flow** — The assistant follows a listen → understand → act → respond loop. Each interaction is self-contained: the device listens, processes one command, responds, and then listens again.
* **Error handling** — Unknown commands get a polite error response instead of silence. This gives the user feedback that the device heard them but couldn't understand, encouraging clearer speech.

3. Experiment
----------------

**Add More Conversation Topics**

Extend the assistant's vocabulary:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Command
     - Response
   * - "How are you"
     - "I'm running at optimal processor temperature, thank you for asking."
   * - "Tell me a joke"
     - "Why did the LED break up with the resistor? It felt too constrained."
   * - "What time is it"
     - Read the system uptime: "I've been running for 12 minutes."

**Challenge: Vision + Voice Fusion**

Enhance "What do you see?" to describe location: "I see a person on the left side of the frame." Use the bounding box coordinates (centerX, centerY from Lesson 3) to determine spatial position.

4. Troubleshooting
--------------------

**Speaker doesn't produce any sound**

* **Cause:** The Multimedia Carrier's speaker is blocked or not connected, or volume is muted.
* **Solution:** Check that nothing is covering the speaker grille on the Carrier. Make sure ``Speaker.begin()`` is called in ``setup()``. Try the volume control if available.

**STT consistently misunderstands commands**

* **Cause:** Speaking too fast, too far from the mic, or with a strong accent.
* **Solution:** Speak clearly and slowly, within 30 cm of the microphone. Check the Monitor to see what text the STT engine is producing — this helps you adjust your pronunciation.

**TTS response is cut off or sounds garbled**

* **Cause:** The next audio capture starts before the TTS finishes speaking.
* **Solution:** Add a delay after ``Speaker.say()`` proportional to the text length: ``delay(response.length() * 100);``. This gives the speaker time to finish before the microphone starts listening again.

**"What do you see" responds with wrong objects**

* **Cause:** The object detection model has low confidence in current lighting or camera angle.
* **Solution:** Make sure the area is well-lit. Point the camera at clearly visible objects within 1–2 meters. The model was trained on common household objects — unusual items may not be recognized.

5. Summary
-------------

Your UNO Q can now hold a conversation! In this lesson, you learned:

* How Speech-to-Text (STT) converts spoken words to text commands
* How Text-to-Speech (TTS) synthesizes spoken responses locally
* How to switch between AI models (voice and vision) within one app
* How to design a conversational listen → process → respond loop

In the next lesson, you'll combine sensor data with AI voice output — building an environment monitor that speaks temperature and humidity readings aloud.
