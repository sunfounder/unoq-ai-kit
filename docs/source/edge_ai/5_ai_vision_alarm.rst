.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

5. AI Vision Alarm
======================

In this lesson, you'll combine the AI vision skills from the previous lessons to build a practical **security system**. The camera continuously monitors its field of view. When a person is detected, the buzzer sounds an alarm and an LED flashes — a simple but effective intruder alert.

In this lesson, you will learn to:

* Run continuous person detection on the camera feed
* Implement a multi-state alarm system (armed / triggered / disarmed)
* Add a cooldown period to prevent repeated alarms
* Build a complete AI-driven security application

1. Build the Circuit
----------------------

**Components Needed**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * :ref:`Arduino Uno Q <cpn_uno_q>`
     - 1 * Multimedia Carrier
     - 1 * Camera Module
     - 1 * :ref:`cpn_led` (Red)
   * - |list_uno_q|
     - |list_uno_q|
     - |list_uno_q|
     - |list_red_led|
   * - 1 * :ref:`cpn_resistor` (220Ω)
     - 1 * :ref:`cpn_buzzer`
     - 1 * :ref:`cpn_button`
     - Several :ref:`cpn_wires`
   * - |list_220ohm|
     - |list_active_buzzer|
     - |list_button|
     - |list_wire|

**Wiring Diagram**

.. image:: img/5_alarm_fritzing.png
   :width: 700
   :align: center

Here are the connections to make:

#. Connect the red LED (with 220Ω resistor) between **digital pin 5** and **GND**.
#. Connect the active buzzer: **VCC** to **digital pin 6**, **GND** to any **GND** pin.
#. Connect the button between **digital pin 3** and **GND** (uses ``INPUT_PULLUP``). This button will arm/disarm the system.
#. Make sure the camera is pointed at the area you want to monitor.

2. Code
----------

**Import the Code**

#. In App Lab, go to **Apps** → **Import App** → **Import from Computer**.

#. Navigate to ``unoq-ai-kit/edge_ai/`` and select ``5_ai_vision_alarm.zip``.

#. Open the imported app.

**Run the Code**

#. Click the **Run** button (▶). The system starts **armed**.

#. Step into the camera's view. After about half a second, the buzzer sounds and the LED flashes rapidly.

#. Press the button to **disarm** the system (LED turns off, buzzer stops). Press again to re-arm.

.. image:: img/5_alarm_result.gif
   :width: 600
   :align: center

**The Code**

.. code-block:: cpp
   :linenos:

   /*
    * Lesson 5: AI Vision Alarm
    * Detects a person and triggers an alarm.
    */

   #include <Arduino_RouterBridge.h>
   #include "camera.h"
   #include "edge_impulse.h"

   const int ledPin = 5;
   const int buzzerPin = 6;
   const int buttonPin = 3;

   bool armed = true;
   bool alarming = false;
   unsigned long alarmStartTime = 0;
   const unsigned long alarmDuration = 5000;  // Alarm for 5 seconds
   const unsigned long cooldown = 10000;      // 10-second cooldown after alarm

   void setup() {
       Monitor.begin();
       Camera.begin();
       AI.begin("person_detection.eim");

       pinMode(ledPin, OUTPUT);
       pinMode(buzzerPin, OUTPUT);
       pinMode(buttonPin, INPUT_PULLUP);

       Monitor.println("System armed");
   }

   void loop() {
       // Check button for arm/disarm toggle
       if (digitalRead(buttonPin) == LOW) {
           delay(50);  // Debounce
           if (digitalRead(buttonPin) == LOW) {
               armed = !armed;
               alarming = false;
               digitalWrite(ledPin, LOW);
               digitalWrite(buzzerPin, LOW);

               Monitor.print("System ");
               Monitor.println(armed ? "armed" : "disarmed");

               while (digitalRead(buttonPin) == LOW);  // Wait for release
           }
       }

       if (!armed) return;  // Nothing to do if disarmed

       // Run person detection
       Camera.capture();
       AIResult result = AI.classify();

       unsigned long now = millis();

       if (result.detected && result.label == "person" && result.confidence > 0.7) {
           if (!alarming && (now - alarmStartTime > cooldown)) {
               alarming = true;
               alarmStartTime = now;
               Monitor.println("INTRUDER DETECTED!");
           }
       }

       // Alarm behavior
       if (alarming) {
           // Flash LED and sound buzzer
           digitalWrite(ledPin, HIGH);
           digitalWrite(buzzerPin, HIGH);
           delay(100);
           digitalWrite(ledPin, LOW);
           digitalWrite(buzzerPin, LOW);
           delay(100);

           // Auto-stop after alarm duration
           if (now - alarmStartTime > alarmDuration) {
               alarming = false;
               alarmStartTime = now;  // Start cooldown
               Monitor.println("Alarm ended — cooling down");
           }
       } else {
           // Armed but no alarm — slow LED pulse to show status
           digitalWrite(ledPin, HIGH);
           delay(50);
           digitalWrite(ledPin, LOW);
           delay(950);
       }
   }

**How it Works**

.. code-block:: text

   States:
       DISARMED → no detection, LED off, buzzer off
       ARMED    → monitoring, LED pulses slowly
       ALARMING → person detected, LED flashes, buzzer sounds
       COOLDOWN → waiting period after alarm ends

   Transitions:
       DISARMED ←→ ARMED: button press
       ARMED → ALARMING: person detected + confidence > 70%
       ALARMING → COOLDOWN: alarm duration expires (5s)
       COOLDOWN → ARMED: cooldown expires (10s)

Here's what's new in this lesson:

* **State machine** — The system has four distinct states (disarmed, armed, alarming, cooldown) with clear transitions between them. State machines are the standard pattern for systems that need different behaviors in different situations.
* **Button toggle** — ``armed = !armed`` flips the boolean value on each press. The ``while (digitalRead(buttonPin) == LOW);`` waits for the button to be released before continuing — this prevents a single press from being read as multiple toggles.
* **Cooldown timer** — After an alarm ends, there's a 10-second cooldown before another alarm can trigger. Without this, the system would immediately re-trigger if the person is still in frame, creating a confusing rapid on/off cycle.
* **Status indication** — When armed but idle, the LED pulses briefly every second. This gives the user visual confirmation that the system is active, without being distracting.

3. Experiment
----------------

**Adjust Sensitivity**

Modify the confidence threshold and detection persistence:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Setting
     - Effect
   * - Confidence ``> 0.5``
     - More sensitive — triggers on partial detections (more false alarms)
   * - Confidence ``> 0.9``
     - Stricter — only triggers on clear person detections (may miss intruders)
   * - Cooldown ``5000``
     - Shorter cooldown — alarm re-arms faster
   * - Alarm ``10000``
     - Longer alarm — intruder is warned for 10 seconds

**Challenge: Silent Arm/Disarm with Gesture**

Replace the button with a gesture: use the gesture recognition model from Lesson 4 to arm/disarm the system with a thumbs-up. Combine two AI models in one app: person detection for monitoring, gesture recognition for control.

4. Troubleshooting
--------------------

**Alarm never triggers, even when a person is clearly visible**

* **Cause:** Confidence threshold is too high, or the person is too far away.
* **Solution:** Lower the confidence threshold to ``0.5``. Move closer to the camera. Make sure the person is well-lit and facing the camera.

**Alarm triggers constantly on nothing**

* **Cause:** False positives — the model sees person-like shapes in the background (coats on hooks, shadows, posters with faces).
* **Solution:** Increase the confidence threshold to ``0.8``. Point the camera at a clean background. Consider adding a minimum detection duration (must detect for 3 consecutive frames before alarming).

**Button doesn't arm/disarm the system**

* **Cause:** Button wiring or debounce issue.
* **Solution:** Check that the button connects pin 3 to GND. The code uses ``INPUT_PULLUP`` — no external resistor needed. Try pressing more firmly.

**System appears frozen after alarm**

* **Cause:** The cooldown timer is active.
* **Solution:** Wait 10 seconds after the alarm stops. The LED will resume slow pulsing when the system is re-armed. To disable cooldown, set ``cooldown = 0``.

5. Summary
-------------

You've built a working AI security system! In this lesson, you learned:

* How to design a multi-state alarm system (armed / alarming / cooldown)
* How to use a button to toggle between system states
* How cooldown timers prevent repeated false triggers
* How to combine continuous AI inference with real-time hardware control

In the next lesson, you'll switch from vision to voice — using spoken commands to control your hardware.
