.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

10. AI Smart Security Camera
================================

This is the **capstone project** of Module D. You'll combine everything you've learned — vision AI, voice control, sensor monitoring, pan-tilt tracking, and alarm systems — into a complete **AI-powered security camera**. When it detects a person, it tracks them, sounds an alarm, and reports what it sees — all running autonomously on the UNO Q.

In this lesson, you will learn to:

* Integrate multiple AI models (person detection + face tracking) in one application
* Build a complete security pipeline: detect → track → alarm → report
* Combine the camera, servo pan-tilt, buzzer, speaker, and DHT11
* Design and implement a complex multi-state embedded AI system

1. Build the Circuit
----------------------

**Components Needed**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * :ref:`Arduino Uno Q <cpn_uno_q>`
     - 1 * Multimedia Carrier
     - 1 * Camera Module
     - 2 * :ref:`cpn_servo`
   * - |list_uno_q|
     - |list_uno_q|
     - |list_uno_q|
     - |list_servo|
   * - 1 * Pan-Tilt Mount
     - 1 * :ref:`cpn_buzzer`
     - 1 * :ref:`cpn_humiture_sensor`
     - Several :ref:`cpn_wires`
   * - |list_uno_q|
     - |list_active_buzzer|
     - |list_dht11|
     - |list_wire|

**Wiring Diagram**

.. image:: img/10_security_camera_fritzing.png
   :width: 700
   :align: center

Here are the connections to make:

#. Assemble the pan-tilt mount with the camera (same as Lesson 3). Connect pan servo to **pin 9**, tilt servo to **pin 10**.

#. Connect the active buzzer: **VCC** to **pin 6**, **GND** to any **GND** pin.

#. Connect the DHT11 module: **VCC** → **5V**, **DATA** → **pin 2**, **GND** → **GND**.

#. All other components (camera, microphone, speaker) are built into the Multimedia Carrier.

2. Code
----------

**Import the Code**

#. In App Lab, go to **My Apps** → **Import App** → **Import from Computer**.

#. Navigate to ``unoq-ai-kit/edge_ai/`` and select ``10_ai_security_camera.zip``.

#. Open the imported app.

**Run the Code**

#. Click the **Run** button (▶). The system starts in **ARMED** mode.

#. The camera pans slowly back and forth, scanning the room.

#. When a person enters the frame:

   * The pan-tilt locks on and **tracks** their face
   * The buzzer sounds an **alarm**
   * The speaker announces: "**Intruder detected**"
   * Temperature and humidity are logged to the Monitor

#. Press the button (on pin 3) to **DISARM** the system.

.. image:: img/10_security_result.gif
   :width: 600
   :align: center

**The Code**

.. code-block:: cpp
   :linenos:

   /*
    * Lesson 10: AI Smart Security Camera
    * Detects intruders, tracks faces, sounds alarm, reports activity.
    */

   #include <Arduino_RouterBridge.h>
   #include <Servo.h>
   #include "camera.h"
   #include "microphone.h"
   #include "speaker.h"
   #include "DHT.h"
   #include "edge_impulse.h"

   // Hardware
   Servo panServo, tiltServo;
   const int panPin = 9, tiltPin = 10;
   const int buzzerPin = 6, buttonPin = 3;
   #define DHTPIN 2
   #define DHTTYPE DHT11
   DHT dht(DHTPIN, DHTTYPE);

   // Tracking
   int panAngle = 90, tiltAngle = 90;
   const float Kp = 0.08;
   int scanDirection = 1;  // 1 = right, -1 = left

   // System state
   enum State { ARMED, TRACKING, ALARMING, DISARMED };
   State state = ARMED;
   unsigned long stateStartTime = 0;
   const unsigned long alarmDuration = 8000;
   const unsigned long cooldown = 15000;
   unsigned long lastEnvReport = 0;
   const unsigned long envInterval = 60000;  // Report environment every minute

   void setup() {
       Monitor.begin();
       Camera.begin();
       Speaker.begin();
       AI.begin("person_detection.eim");

       panServo.attach(panPin); panServo.write(90);
       tiltServo.attach(tiltPin); tiltServo.write(90);
       pinMode(buzzerPin, OUTPUT);
       pinMode(buttonPin, INPUT_PULLUP);
       dht.begin();

       Speaker.say("Security system active.");
       stateStartTime = millis();
   }

   void loop() {
       unsigned long now = millis();

       // Button: toggle arm/disarm
       if (digitalRead(buttonPin) == LOW) {
           delay(50);
           if (digitalRead(buttonPin) == LOW) {
               state = (state == DISARMED) ? ARMED : DISARMED;
               Speaker.say(state == ARMED ? "Armed" : "Disarmed");
               while (digitalRead(buttonPin) == LOW);
           }
       }

       if (state == DISARMED) return;

       // Environment monitoring (background task)
       if (now - lastEnvReport >= envInterval) {
           lastEnvReport = now;
           float t = dht.readTemperature();
           float h = dht.readHumidity();
           if (!isnan(t) && !isnan(h)) {
               Monitor.print("Env: "); Monitor.print(t);
               Monitor.print("C, "); Monitor.print(h); Monitor.println("%");
           }
       }

       // Camera + AI
       Camera.capture();
       AIResult result = AI.classify();

       // State machine
       switch (state) {
           case ARMED:
               // Scanning: sweep pan servo back and forth
               panAngle += scanDirection * 2;
               if (panAngle >= 150) scanDirection = -1;
               if (panAngle <= 30)  scanDirection = 1;
               panServo.write(panAngle);
               tiltServo.write(90);

               // Person detected → start tracking
               if (result.detected && result.label == "person" && result.confidence > 0.6) {
                   state = TRACKING;
                   stateStartTime = now;
                   Monitor.println("TRACKING: Person detected");
               }
               break;

           case TRACKING:
               // Track the person with pan-tilt
               if (result.detected) {
                   float errorX = result.centerX - 0.5;
                   float errorY = result.centerY - 0.5;
                   panAngle += errorX * Kp * 180;
                   tiltAngle -= errorY * Kp * 180;
                   panAngle = constrain(panAngle, 0, 180);
                   tiltAngle = constrain(tiltAngle, 30, 150);
                   panServo.write(panAngle);
                   tiltServo.write(tiltAngle);
               }

               // Alarm after 2 seconds of tracking
               if (now - stateStartTime > 2000) {
                   state = ALARMING;
                   stateStartTime = now;
                   Speaker.say("Intruder detected!");
                   Monitor.println("ALARM!");
               }
               break;

           case ALARMING:
               // Flash buzzer rapidly
               digitalWrite(buzzerPin, (millis() / 150) % 2);

               // End alarm after duration
               if (now - stateStartTime > alarmDuration) {
                   digitalWrite(buzzerPin, LOW);
                   state = ARMED;
                   stateStartTime = now;  // Begin cooldown
                   Speaker.say("Alarm ended. Re-arming.");
               }
               break;
       }
   }

**How it Works**

.. code-block:: text

   States:
       DISARMED  → no monitoring, all outputs off
       ARMED     → scanning: pan servo sweeps, waiting for detection
       TRACKING  → person seen: pan-tilt follows them, preparing to alarm
       ALARMING  → buzzer sounds, speaker announces intruder
       → returns to ARMED after alarm ends + cooldown

   Key design patterns:
       - State machine: each state has distinct behavior
       - Multi-model: person detection (vision) + DHT11 (sensor)
       - Multi-output: pan-tilt servos + buzzer + speaker + Monitor
       - Background tasks: environment logging runs independently of security

Here's how the capstone integrates concepts from every previous lesson:

* **Lesson 1**: Object detection model identifies people
* **Lesson 3**: Pan-tilt tracking follows the detected face
* **Lesson 5**: State machine (armed/alarming/disarmed) with cooldown
* **Lesson 7**: TTS speaker output ("Intruder detected!")
* **Lesson 8**: DHT11 environment monitoring running as a background task
* **Lesson 9**: Custom-trained models can replace the pre-trained ones

3. Experiment
----------------

**Add Two-Way Voice Control**

Integrate the voice command model from Lesson 6 to arm/disarm the system with spoken commands: "Arm security" and "Disarm security". This makes the system fully hands-free.

**Challenge: Event Logging**

Log every security event (detection time, alarm duration, environment readings) to the Monitor in a structured format. Later, you can export this log for analysis:

.. code-block:: cpp

   Monitor.print(millis() / 1000);  // seconds since boot
   Monitor.print(",EVENT,");
   Monitor.println("person_detected");

**Challenge: Email or Telegram Alert**

If your UNO Q is connected to Wi-Fi (Module B), send a Telegram notification when the alarm triggers. Combine the AI security pipeline from this lesson with the IoT skills from Module B.

4. Troubleshooting
--------------------

**System is too slow — tracking lags behind the person**

* **Cause:** Running multiple AI models and sensor reads in sequence creates latency.
* **Solution:** Reduce camera resolution to 320×240. Remove the environment monitoring if not needed. Consider increasing the tracking Kp to compensate for latency.

**False alarms trigger frequently**

* **Cause:** The person detection model is too sensitive for your environment.
* **Solution:** Increase the confidence threshold to ``0.75``. Add a minimum detection duration — require 3 consecutive person detections before entering TRACKING state.

**Speaker announcements overlap or cut each other off**

* **Cause:** Multiple ``Speaker.say()`` calls happening close together.
* **Solution:** Add a ``speakerBusy`` flag that prevents new announcements while one is playing. Check ``Speaker.isPlaying()`` before calling ``Speaker.say()``.

**Servos jitter or make noise when idle**

* **Cause:** The servo receives continuous small position adjustments from tracking noise.
* **Solution:** Add a dead zone (as shown in Lesson 3). If the tracking error is very small (<2% offset), skip the servo update. You can also call ``servo.detach()`` when not tracking to prevent idle jitter.

5. Summary
-------------

Congratulations! You've built a complete AI security camera — the most complex project in the entire course. In this lesson, you integrated:

* Person detection and face tracking from vision AI
* Pan-tilt servo control for physical camera movement
* Multi-state alarm logic with cooldown and arm/disarm
* Text-to-Speech for audible alerts
* Environmental monitoring as a background task

This project demonstrates what's possible when you combine the hardware skills from Module A, the connectivity options from Module B, the LLM integration from Module C, and the edge AI capabilities from Module D.

You've come a long way from blinking an LED. Your UNO Q can now see, hear, speak, track, monitor, and respond — a truly intelligent device, built by you.
