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

2. Run the App
----------------

#. Open **Arduino App Lab**, go to **Apps**. Click the dropdown arrow next to **Create new app +** and select **Import App**.

   .. image:: /img/app_import_app.png
      :width: 600
      :align: center

#. Select **Import from Computer**.

   .. image:: /img/app_import_pc.png
      :width: 600
      :align: center

#. Download :download:`02 Face Alarm.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/02.Face.Alarm.zip>` and import it in App Lab.

#. The app appears in **Apps** — click it to open.

#. With the app open, click the **Run** button (▶) in the top-right corner. The app boots the camera and loads the face-detection model, which takes a few seconds the first time.

   .. image:: /img/app_run.png
      :width: 500
      :align: center

#. The Output window prints:

   *"🚨 Face Alarm running — show your face to the camera!"*

   A **Web UI** tab opens automatically, showing the live camera feed with the status *"No face — Alarm OFF"* below it.

#. Position yourself in front of the camera and face it. Within a moment the status flips to *"🚨 Face detected — Alarm ON"*, the hint text changes to *"The buzzer is sounding!"*, and the buzzer starts beeping rapidly — short bursts, about 150 ms on and 150 ms off.

#. Step away so your face is out of the frame. The alarm keeps sounding for about two more seconds — the app gives a face a grace period in case you simply turned away for a moment — and then stops. The status returns to *"No face — Alarm OFF"*.

**How it Works**

One AI decision now reaches out of the screen and into the real world, and the work is split the way the UNO Q's two processors are built for it: Python on the Linux MPU decides *whether there is a face*, while the sketch on the STM32 MCU decides *how the buzzer behaves*.

* ``02 Face Alarm/`` — the app folder

  * ``app.yaml`` — app metadata and the Bricks it declares (``web_ui`` and ``video_object_detection`` with ``model: face-detection``)
  * ``README.md`` — project documentation and usage guide

  * ``python/``

    * ``main.py`` — face detection, alarm state, and the Web UI

  * ``sketch/``

    * ``sketch.ino`` — buzzer control and the two Bridge functions Python calls
    * ``sketch.yaml`` — sketch configuration

  * ``assets/``

    * ``index.html`` — Web UI structure: the camera card and the face status line
    * ``app.js`` — browser logic: socket events and status text
    * ``style.css`` — visual styling
    * ``libs/socket.io.min.js`` — Socket.IO client library
    * ``img/sf_logo.png`` — header logo

The data path from a face in front of the lens to a buzzer that sounds:

.. mermaid::

   sequenceDiagram
       participant C as Camera (CSI)
       participant P as Python (main.py)
       participant S as Sketch (sketch.ino)
       participant B as Browser (HTML/JS)

       C->>P: frame
       P->>P: VideoObjectDetection — face-detection model, confidence 0.5, debounce 0.5 s
       P->>P: on_detect("face") → face_detected()
       P->>S: Bridge.call("alarm_on")
       S->>S: beep D5 — 150 ms on, 150 ms off
       P-->>B: socket.io "face_status" — detected
       P->>P: monitor thread — checks every 0.2 s
       P->>S: Bridge.call("alarm_off") — no face for 2.0 s
       S->>S: stop the buzzer
       P-->>B: socket.io "face_status" — no face

Here's what each component does:

**Sketch (sketch.ino)** — runs on the STM32 MCU
  * ``Bridge.provide("alarm_on", alarm_on)`` and ``Bridge.provide("alarm_off", alarm_off)`` register the two functions Python can call
  * ``alarm_on()`` raises the ``alarmActive`` flag; ``alarm_off()`` clears it and immediately drives the pin low
  * ``loop()`` beeps ``buzzerPin`` (D5) — 150 ms high, 150 ms low, over and over — while the flag is set, and idles when it is not

**Python (main.py)** — runs on the Linux MPU
  * ``VideoObjectDetection(camera, confidence=0.5, debounce_sec=0.5)`` runs the ``face-detection`` model declared in ``app.yaml``
  * ``detection.on_detect("face", face_detected)`` fires only for the class this project cares about
  * ``Bridge.call("alarm_on")`` and ``Bridge.call("alarm_off")`` command the sketch
  * ``ui.send_message("face_status", ...)`` tells the browser whether a face is present
  * A background thread watches the clock so the alarm silences itself

**Bridge** — communication channel between MPU and MCU
  * Sketch side: ``Bridge.provide("name", function)`` exposes a function
  * Python side: ``Bridge.call("name")`` invokes it — this is RPC across the two processors

**Browser (HTML/JS)** — runs in the user's browser
  * ``socket.on('face_status', ...)`` flips the status between "🚨 Face detected — Alarm ON" and "No face — Alarm OFF"
  * The live video arrives on its own channel, in an ``<iframe>`` pointed at port 4912 ``/embed``

**The sketch owns the buzzer** — the two Bridge functions are tiny: they only set or clear a flag. The real work happens back in ``loop()``, which sleeps while the flag is clear and otherwise toggles ``buzzerPin`` (D5) on and off every 150 ms — the rapid beep you heard. Because ``alarm_off()`` also writes the pin low, the buzzer falls silent instantly, even in the middle of a beep.

**Python asks for the alarm** — the AI side follows the pattern from the previous project with two differences. First, the model: ``app.yaml`` requests ``video_object_detection`` with ``model: face-detection``, a model specialized for faces rather than the general object model. Second, the listener: instead of ``on_detect_all`` (every object, every frame), Python registers ``on_detect("face", ...)``, which fires only for the single class the project cares about. The settings are tuned more strictly — ``confidence=0.5`` means a face must score at least 50% before it counts, and ``debounce_sec=0.5`` paces the callbacks.

**The first-sighting latch** — the brick may call ``face_detected()`` again and again while a face stays in view, and the function must not flood the Bridge with ``alarm_on`` calls, so a ``face_visible`` flag turns it into a latch: the first sighting refreshes the timestamp and calls ``Bridge.call("alarm_on")``, while every later sighting only updates the timestamp and returns early. The alarm turns on exactly once, and the browser is told so the page can flip to "🚨 Face detected — Alarm ON".

**The watchdog thread** — someone has to notice when the face is *gone*, and that cannot happen in the detection callback because it only fires when a face is seen. So Python starts a background thread: every 0.2 seconds it wakes up, and if a face was seen but the last sighting is more than 2.0 seconds ago, it clears the latch, calls ``Bridge.call("alarm_off")``, and tells the Web UI the alarm is off. That is the two-second grace period you felt — step out of frame briefly and the alarm keeps going; stay away and it stops. Both threads touch ``face_visible``, so every access is guarded by a lock to keep them from stepping on each other.

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
