.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

6. Voice Control System
===========================

In Lesson 2, your UNO Q learned to hear a single wake word. Now it will understand **multiple spoken commands**. Say "turn on the light" and the LED lights up. Say "sound the alarm" and the buzzer activates. Say "look left" and the servo turns. Voice control — no keyboard, no button, no touch required.

In this lesson, you will learn to:

* Run a multi-keyword voice command model
* Parse different voice commands and map them to hardware actions
* Control an LED, buzzer, and servo with spoken instructions
* Handle background noise and false triggers in a voice interface

1. Build the Circuit
----------------------

**Components Needed**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * :ref:`Arduino Uno Q <cpn_uno_q>`
     - 1 * Multimedia Carrier
     - 1 * :ref:`cpn_led` (Red)
     - 1 * :ref:`cpn_resistor` (220Ω)
   * - |list_uno_q|
     - |list_uno_q|
     - |list_red_led|
     - |list_220ohm|
   * - 1 * :ref:`cpn_buzzer`
     - 1 * :ref:`cpn_servo`
     - Several :ref:`cpn_wires`
     - 1 * :ref:`cpn_breadboard`
   * - |list_active_buzzer|
     - |list_servo|
     - |list_wire|
     - |list_breadboard|

**Wiring Diagram**

.. image:: img/6_voice_control_fritzing.png
   :width: 700
   :align: center

Here are the connections to make:

#. Connect the red LED (with 220Ω resistor) between **digital pin 5** and **GND**.
#. Connect the active buzzer: **VCC** to **digital pin 6**, **GND** to any **GND** pin.
#. Connect the servo: signal wire to **digital pin 9**, power to **5V**, ground to **GND**.

2. Code
----------

**Import the Code**

#. In App Lab, go to **My Apps** → **Import App** → **Import from Computer**.

#. Navigate to ``unoq-ai-kit/edge_ai/`` and select ``6_ai_voice_control.zip``.

#. Open the imported app.

**Run the Code**

#. Click the **Run** button (▶).

#. Speak these commands clearly toward the Multimedia Carrier:

   * **"Turn on the light"** → LED turns on
   * **"Turn off the light"** → LED turns off
   * **"Sound the alarm"** → Buzzer beeps three times
   * **"Look left"** → Servo rotates to 45°
   * **"Look right"** → Servo rotates to 135°
   * **"Look center"** → Servo returns to 90°

.. image:: img/6_voice_control_result.gif
   :width: 600
   :align: center

**The Code**

.. code-block:: cpp
   :linenos:

   /*
    * Lesson 6: Voice Control System
    * Recognizes voice commands and controls multiple hardware outputs.
    */

   #include <Arduino_RouterBridge.h>
   #include <Servo.h>
   #include "microphone.h"
   #include "edge_impulse.h"

   Servo myServo;

   const int ledPin = 5;
   const int buzzerPin = 6;
   const int servoPin = 9;

   String lastCommand = "";
   unsigned long lastCommandTime = 0;
   const unsigned long commandTimeout = 2000;  // Ignore repeats for 2s

   void setup() {
       Monitor.begin();
       Microphone.begin();
       AI.begin("voice_commands.eim");

       pinMode(ledPin, OUTPUT);
       pinMode(buzzerPin, OUTPUT);

       myServo.attach(servoPin);
       myServo.write(90);  // Center
   }

   void executeCommand(String command) {
       Monitor.print("Command: ");
       Monitor.println(command);

       if (command == "turn_on_light") {
           digitalWrite(ledPin, HIGH);
       }
       else if (command == "turn_off_light") {
           digitalWrite(ledPin, LOW);
       }
       else if (command == "sound_alarm") {
           for (int i = 0; i < 3; i++) {
               digitalWrite(buzzerPin, HIGH);
               delay(150);
               digitalWrite(buzzerPin, LOW);
               delay(100);
           }
       }
       else if (command == "look_left") {
           myServo.write(45);
       }
       else if (command == "look_right") {
           myServo.write(135);
       }
       else if (command == "look_center") {
           myServo.write(90);
       }
   }

   void loop() {
       Microphone.capture(1500);  // 1.5 seconds of audio
       AIResult result = AI.classify();

       unsigned long now = millis();

       if (result.detected && result.confidence > 0.7) {
           // Prevent the same command from executing repeatedly
           if (result.label != lastCommand ||
               (now - lastCommandTime > commandTimeout)) {

               executeCommand(result.label);

               lastCommand = result.label;
               lastCommandTime = now;
           }
       }
   }

**How it Works**

.. code-block:: text

   loop() → runs forever:
       Record 1.5s of audio → classify
       Command detected with >70% confidence?
           YES → is it different from last command
                 OR has 2s passed since last command?
               YES → execute the matching action
               NO  → ignore (same command, too soon)

   Command mapping:
       turn_on_light  → LED ON
       turn_off_light → LED OFF
       sound_alarm    → buzzer beeps 3 times
       look_left      → servo 45°
       look_right     → servo 135°
       look_center    → servo 90°

Here's what's new in this lesson:

* **Multi-command model** — Unlike the binary keyword spotter in Lesson 2, this model classifies audio into **six categories** (five commands plus background noise). Each category maps to a different action.
* **Command deduplication** — ``lastCommand`` and ``commandTimeout`` prevent the same command from executing repeatedly. Without this, saying "turn on the light" once could trigger the command on every 1.5-second window while you're still speaking. The timeout ensures at least 2 seconds between identical commands.
* **Helper function ``executeCommand()``** — Separating command logic from detection logic makes the code cleaner. ``loop()`` handles audio capture and classification; ``executeCommand()`` handles the hardware actions. To add a new voice command, you only need to add one ``else if`` branch.
* **Servo as voice-controlled actuator** — Voice commands can control anything, not just on/off devices. The servo demonstrates proportional control — "look left" and "look right" set specific angles, not just binary states.

3. Experiment
----------------

**Add a New Command**

Add a "blink" command that makes the LED blink 5 times rapidly:

.. code-block:: cpp

   else if (command == "blink") {
       for (int i = 0; i < 5; i++) {
           digitalWrite(ledPin, HIGH);
           delay(100);
           digitalWrite(ledPin, LOW);
           delay(100);
       }
   }

**Challenge: Voice + Gesture Combo**

Combine voice commands with gesture control from Lesson 4: use voice for mode selection ("activate lights", "activate motion") and gestures for fine control (thumbs up/down for brightness).

**Challenge: Confidence Logging**

Print all six confidence scores to the Monitor every cycle, not just the winning label. Observe how the scores change when you speak softly vs. loudly, near vs. far. This helps you understand the model's uncertainty.

4. Troubleshooting
--------------------

**One command triggers another command's action**

* **Cause:** Similar-sounding commands are being confused by the model.
* **Solution:** Increase the confidence threshold to ``0.8``. Speak more distinctly. If the problem persists, the model may need additional training data for the confused command pair.

**Same command triggers twice from one spoken phrase**

* **Cause:** The ``commandTimeout`` is too short, or ``lastCommand`` isn't being set correctly.
* **Solution:** Increase ``commandTimeout`` to ``3000`` (3 seconds). Make sure ``lastCommand = result.label;`` runs after ``executeCommand()``.

**Commands work but feel slow to respond**

* **Cause:** The 1.5-second capture window plus inference adds latency.
* **Solution:** This is expected. Total round-trip from speech to action is about 1.5–2 seconds. For faster response, reduce ``Microphone.capture()`` to 1000ms, but shorter windows may reduce accuracy.

**Background conversations trigger commands**

* **Cause:** The model hears command-like words in normal speech.
* **Solution:** Increase confidence threshold, or add a wake word requirement (combine with Lesson 2's keyword spotter — only listen for commands after "Hello Arduino" is detected).

5. Summary
-------------

Your UNO Q now responds to your voice! In this lesson, you learned:

* How a multi-command voice model classifies spoken instructions
* How to map different voice commands to different hardware actions
* How to prevent command duplication with timeout logic
* How to separate detection logic from execution logic for cleaner code

In the next lesson, you'll go beyond simple commands — building a two-way AI voice assistant that listens AND speaks back.
