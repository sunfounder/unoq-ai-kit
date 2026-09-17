.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

02 Face Alarm
===============

In the previous project the AI *watched* — it recognized objects and reported them on screen, but nothing happened beyond the Web UI. This lesson crosses that line: the moment the camera sees a face, a buzzer on the breadboard starts sounding an alarm, and when the face leaves, the alarm stops by itself. This is the first time in this module that an AI decision directly drives physical hardware — the AI sees, decides, and acts.

.. image:: img/02_face_alarm.png
   :width: 600
   :align: center

In this lesson, you will learn to:

* Detect faces with the dedicated ``face-detection`` model
* Trigger the buzzer from Python through a ``Bridge.call()``
* Track how long a face has been absent, and stop the alarm automatically
* Follow a complete AI loop: camera → model → Python → sketch → hardware

1. Setup
-----------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * Active :ref:`cpn_buzzer`
     - 1 * :ref:`cpn_breadboard`
     - Several :ref:`cpn_wires`
   * - |list_pan_tilt|
     - |list_active_buzzer|
     - |list_breadboard|
     - |list_wire|
   * - 1 * USB-C Cable
     - -
     - -
     - -
   * - |list_usb_cable|
     - -
     - -
     - -

.. note::

   Before using the camera, make sure external carriers are enabled on your UNO Q — this is a one-time setup: :ref:`enable_external_carriers`.

**Wiring Diagram**

Connect the active buzzer between **D5** and **GND**: the buzzer is polarized, so its **+** pin (or longer leg) goes to D5 and its **−** pin (or shorter leg) to GND, routed through the breadboard with jumper wires. The sketch drives the pin high and low to make it beep, so no extra resistor or transistor is needed.

.. image:: /img/wiring/wiring_ac_buzzer.png
   :width: 500
   :align: center

2. Code
----------

**Import the Code**

#. Open **Arduino App Lab**, go to **Apps**. Click the dropdown arrow next to **Create new app +** and select **Import App**.

   .. image:: /img/app_import_app.png
      :width: 600
      :align: center

#. Select **Import from Computer**.

   .. image:: /img/app_import_pc.png
      :width: 600
      :align: center

#. Navigate to the ``unoq-ai-kit/edge_ai/`` folder and select ``02 Face Alarm.zip``.

#. The app appears in **Apps** — click it to open.

**Run the Code**

#. With the app open, click the **Run** button (▶) in the top-right corner. The app boots the camera and loads the face-detection model, which takes a few seconds the first time.

   .. image:: /img/app_run.png
      :width: 500
      :align: center

#. The Output window prints:

   *"🚨 Face Alarm running — show your face to the camera!"*

   A **Web UI** tab opens automatically, showing the live camera feed with the status *"No face — Alarm OFF"* below it.

#. Position yourself in front of the camera and face it. Within a moment the status flips to *"🚨 Face detected — Alarm ON"*, the hint text changes to *"The buzzer is sounding!"*, and the buzzer starts beeping rapidly — short bursts, about 150 ms on and 150 ms off.

#. Step away so your face is out of the frame. The alarm keeps sounding for about two more seconds — the app gives a face a grace period in case you simply turned away for a moment — and then stops. The status returns to *"No face — Alarm OFF"*.

**The Code**

**Sketch (sketch.ino)** — runs on the STM32 MCU and owns the buzzer

.. code-block:: cpp
   :linenos:

   /*
    * Face Alarm
    *
    * Bridge commands from Python:
    *   alarm_on()  → starts beeping
    *   alarm_off() → stops
    *
    * Pattern: short beeps repeating while alarm is active.
    */

   #include <Arduino_RouterBridge.h>

   const int buzzerPin = 5;

   bool alarmActive = false;

   void alarm_on()  { alarmActive = true; }
   void alarm_off() { alarmActive = false; digitalWrite(buzzerPin, LOW); }

   void setup() {
       pinMode(buzzerPin, OUTPUT);
       digitalWrite(buzzerPin, LOW);

       Bridge.begin();
       Bridge.provide("alarm_on", alarm_on);
       Bridge.provide("alarm_off", alarm_off);
   }

   void loop() {
       if (!alarmActive) {
           delay(100);
           return;
       }

       // Rapid beep pattern
       digitalWrite(buzzerPin, HIGH);
       delay(150);
       digitalWrite(buzzerPin, LOW);
       delay(150);
   }

**Python (main.py)** — runs on the Linux MPU: face detection, alarm state, and Web UI

.. code-block:: python
   :linenos:

   # SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
   #
   # SPDX-License-Identifier: MPL-2.0

   """
   Face Alarm — sound a buzzer when a face is detected.

   When the camera sees a face, Python tells the sketch to turn on
   the buzzer via Bridge. When the face disappears, the buzzer stops.
   This is the first time AI controls physical hardware.
   """

   import threading
   import time
   from datetime import datetime, UTC

   from arduino.app_utils import App, Bridge
   from arduino.app_bricks.web_ui import WebUI
   from arduino.app_bricks.video_objectdetection import VideoObjectDetection
   from arduino.app_peripherals.camera import Camera

   ui = WebUI()

   camera = Camera(adjustments=lambda frame: frame[::-1, :])
   camera.start()

   detection = VideoObjectDetection(
       camera,
       confidence=0.5,
       debounce_sec=0.5,
   )

   face_visible = False
   last_face_time = 0.0
   face_lock = threading.Lock()
   FACE_LOST_TIMEOUT = 2.0  # seconds before turning off alarm


   def face_detected():
       """Called by the brick every time a face is seen."""
       global face_visible, last_face_time

       with face_lock:
           last_face_time = time.monotonic()

           if face_visible:
               return  # Already alarming, just refresh the timer

           face_visible = True

       # First time we see a face → activate the buzzer
       Bridge.call("alarm_on")

       ui.send_message("face_status", {
           "detected": True,
           "text": "Face detected — Alarm ON",
           "timestamp": datetime.now(UTC).isoformat(),
       })


   def monitor_face():
       """Background thread: turn off alarm if face is lost for too long."""
       global face_visible

       while True:
           should_off = False

           with face_lock:
               if face_visible:
                   elapsed = time.monotonic() - last_face_time
                   if elapsed >= FACE_LOST_TIMEOUT:
                       face_visible = False
                       should_off = True

           if should_off:
               Bridge.call("alarm_off")

               ui.send_message("face_status", {
                   "detected": False,
                   "text": "No face — Alarm OFF",
                   "timestamp": datetime.now(UTC).isoformat(),
               })

           time.sleep(0.2)


   detection.on_detect("face", face_detected)

   # Start background monitor thread
   status_thread = threading.Thread(target=monitor_face, daemon=True)
   status_thread.start()

   print("🚨 Face Alarm running — show your face to the camera!")

   App.run()

**How it Works**

.. code-block:: text

   camera frames → face-detection model (confidence ≥ 0.5, debounce 0.5 s)
       → on_detect("face") → face_detected() — first sighting only
           → Bridge.call("alarm_on") → sketch beeps 150 ms on / 150 ms off
           → ui.send_message("face_status", detected: True)
   monitor thread checks every 0.2 s:
       face gone for ≥ 2.0 s → Bridge.call("alarm_off") → buzzer stops
           → ui.send_message("face_status", detected: False)

This project is a two-process team, and the work is split exactly the way the two processors of the UNO Q are good at it. On the Linux MPU, Python decides *whether there is a face*. On the STM32 MCU, the sketch decides *how the buzzer should behave*. Between them runs the same RouterBridge pattern you met in the earlier web-UI projects — but with a new twist: this time Python is the caller and the sketch is the servant.

**The sketch owns the buzzer** — ``alarm_on()`` and ``alarm_off()`` are tiny functions registered with ``Bridge.provide()`` in ``setup()``. The real work happens in ``loop()``: while ``alarmActive`` is false it just sleeps, but once the flag is set it drives ``buzzerPin`` (D5) high for 150 ms and low for 150 ms, over and over — the rapid beep you heard. Because ``alarm_off()`` also calls ``digitalWrite(buzzerPin, LOW)``, the buzzer goes silent instantly when Python calls it, even in the middle of a beep.

**Python asks for the alarm** — the AI side is nearly identical to the previous project, with two differences. First, the model: ``app.yaml`` requests ``video_object_detection`` with ``model: face-detection``, a model specialized for faces rather than the general object model. Second, the listener: instead of ``on_detect_all`` (every object, every frame), the code registers ``detection.on_detect("face", face_detected)``, which only fires for the single class the project cares about. The settings are tuned a bit more strictly — ``confidence=0.5`` means a face must score at least 50% before it counts, and ``debounce_sec=0.5`` paces the callbacks.

**The first-sighting latch** — when a face appears, the brick may call ``face_detected()`` repeatedly. The function must not spam Bridge with ``alarm_on`` calls, so a ``face_visible`` flag turns it into a latch: the first sighting sets the flag, refreshes ``last_face_time``, and calls ``Bridge.call("alarm_on")`` — every later sighting simply updates the timestamp and returns early. The alarm is turned on exactly once, and the Web UI receives a ``face_status`` message so the page can flip to "🚨 Face detected — Alarm ON".

**The watchdog thread** — someone has to notice when the face is *gone*. That cannot happen in the detection callback (it only fires when a face is seen), so Python starts a background thread. Every 0.2 seconds ``monitor_face()`` wakes up, and if a face was seen but the last sighting is more than ``FACE_LOST_TIMEOUT`` (2.0 s) ago, it clears the latch, calls ``Bridge.call("alarm_off")``, and tells the Web UI the alarm is off. This is the two-second grace period you felt: step out of frame briefly and the alarm keeps going; stay away and it stops. Both threads touch ``face_visible``, so every access is guarded by ``face_lock`` to keep them from stepping on each other.

3. Experiment
----------------

**Test the Alarm's Behavior**

The alarm has a clear on-condition (a face above 50% confidence) and a timer-based off-condition. Probe both:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - You do
     - Result
   * - Show your face to the camera
     - Buzzer starts beeping rapidly; Web UI shows "🚨 Face detected — Alarm ON"
   * - Step out of view for about one second, then come back
     - The buzzer never stops — the alarm refreshes as long as faces keep being seen
   * - Step out of view and stay away
     - The buzzer stops about two seconds after the last sighting; UI returns to "No face — Alarm OFF"
   * - Face the camera and slowly back away
     - Eventually the alarm stops — at that distance the model's confidence drops below 50%
   * - Turn your head so only your profile is visible
     - Detection becomes less reliable; the alarm may flicker on and off

**Challenge: Find the Face-Detection Envelope**

A face detector has its own comfort zone of distance, angle, and light. Walk backward slowly, step by step, until the alarm refuses to trigger, then walk forward again — note roughly how far that point is. Try the same test in dim light and with a light behind you, and notice whether the reliable distance shrinks. Finally, hold up a photo of a face or a face drawn on paper: does the model treat it as a face? An AI detector works on visual patterns, not on consciousness — finding where the pattern breaks is the point of the experiment.

4. Troubleshooting
--------------------

**The Web UI shows the alarm is ON, but the buzzer is silent**

* **Cause:** The buzzer is not connected to D5, or its + and − pins are swapped.
* **Solution:** Check the wiring: the + pin goes to D5 and the − pin to GND. If the legs are swapped the buzzer cannot sound. Confirm the jumper wires are seated firmly in the breadboard.

**The buzzer never sounds, even when you face the camera**

* **Cause:** Your face is too far, too small, or too dim for the model to reach the 50% confidence threshold — or the model was still loading in the first seconds after Run.
* **Solution:** Sit 30–60 cm away, face the camera squarely, and keep the room lit. Wait a few seconds after the app starts before testing. Watch the Web UI: if the status never flips to "Face detected — Alarm ON", the model is not seeing a confident face.

**The alarm triggers when nobody is there**

* **Cause:** The face detector matched a face-like pattern — a photo, a poster, a face on a phone screen, or a strong shadow — at 50% or higher confidence.
* **Solution:** Move or remove the face-like object, or turn the camera away from it. Remember the model reports patterns, not intentions — a confident guess is still a guess.

**The alarm keeps buzzing long after you leave the frame**

* **Cause:** Something the model reads as a face is still in view. Every new detection refreshes the 2-second timer, so the alarm can keep itself alive indefinitely.
* **Solution:** Check the frame for face-like objects near the edge of the view (a person passing behind you, your own hand, a screen). When the view is truly empty of faces, the alarm stops about two seconds after the last detection.

5. Summary
-------------

Congratulations — your AI has left the screen and touched the physical world! The face appeared, the model decided, Python called Bridge, and a buzzer physically sounded. You have now seen the complete AI loop that this module is built around:

* A dedicated ``face-detection`` model watches every frame at 50% confidence
* ``on_detect("face", ...)`` fires only for faces, and a latch makes sure the alarm turns on exactly once
* ``Bridge.call("alarm_on")`` and ``Bridge.call("alarm_off")`` let Python command the sketch, which beeps D5 at 150 ms on / 150 ms off
* A background watchdog thread gives a face two seconds of grace before silencing the alarm

The buzzer answered a yes-or-no question: is there a face? In the next project the AI will answer a richer one — not just *whether* something is there, but *what* it is — and the answer will pick a color for an LED.
