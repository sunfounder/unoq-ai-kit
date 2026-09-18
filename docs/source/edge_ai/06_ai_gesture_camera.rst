.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

06 AI Gesture Camera
====================

In the previous project, the AI counted what the camera saw — but the only thing that changed was a number on a page. Nothing in the room moved. This project hands over the controls: **your hand becomes the remote**. A thumbs up tilts the camera up, a fist tilts it down, an open hand sends the pan-tilt back to center, and a V-sign takes a photo. Every gesture also answers you out loud — *"Moving up."*, *"Photo taken."* — so you always know the board understood. The real lesson, though, is not the gestures. It is teaching the UNO Q to tell a **deliberate gesture** apart from a hand that simply happens to be in front of the lens.

.. image:: img/06_ai_gesture_camera.png
   :width: 600
   :align: center

In this lesson, you will learn to:

* Run the ``VideoObjectDetection`` brick with its **hand-gestures** model and read the labels it produces
* Turn one gesture into one physical action: a 5° tilt step, a centering move, a photo, or a spoken reply
* Build a **gesture state machine** — a stable window, a lock, and a re-arm rule — so a gesture fires exactly once
* Keep the AI detection callback fast by handing servo, disk, and speech work to a background worker

1. Setup
----------

**What You Need**

.. list-table::
   :widths: 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * USB-C Cable
   * - |list_pan_tilt|
     - |list_usb_cable|

The kit is complete as it comes: the camera is built into the Multimedia Carrier, the two servos already carry the pan-tilt bracket, and the carrier's speaker does the talking. The one thing this project asks for is power — two servos moving under load draw more than the USB port can supply, so you will connect the battery pack to the Robot Shield before running the app.

.. note::

   Before using the camera, make sure external carriers are enabled on your UNO Q — this is a one-time setup: :ref:`enable_external_carriers`.

**Wiring Diagram**

Plug the pan servo's signal lead into **D9** and the tilt servo's into **D10**, and make sure both servos are powered from the Robot Shield's **5 V** and **GND** servo headers, because two servos moving under load draw far more current than a signal pin could ever supply.

.. image:: /img/wiring/wiring_pan_tilt.png
   :width: 600
   :align: center

2. Run the App
----------------

#. Download :download:`06 AI Gesture Camera.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/06.AI.Gesture.Camera.zip>`.
#. In App Lab, go to **Apps** → **Create new app** → **Import App** → **Import from Computer**, and open the package you downloaded.
#. The app appears in **Apps** — click it to open.

#. The servos and the camera together draw more power than the USB port alone can provide, so connect the battery pack to the Robot Shield.

#. Click the **Run** button (▶). The pan-tilt swings to its center position — pan at 90° and tilt at 85° — and the Console prints ``AI Gesture Camera is running.``

#. While the speech engine prepares itself, the Console prints ``[TTS] Ready.``

   .. note::

      The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

#. Open the **Web UI** tab. The live camera feed fills the card, the gesture panel reads **Current Gesture: Waiting...** with no confidence yet, and the hint line reminds you of the four moves: 👍 Move up · ✊ Move down · ✌️ Take photo · 🖐️ Center pan-tilt.

#. Hold up a **thumbs up**, roughly 50 cm from the camera, with your whole hand inside the frame and a plain background behind it. Keep it steady for about 0.6 seconds. The panel switches to **Thumbs up** with a confidence percentage, the tilt servo lifts the camera one 5° step (85° → 80°) and answers *"Moving up."*, and the last-action line adds *"— remove your hand"*. Each further thumbs up takes another 5° step, until the tilt reaches **60°** — the highest position — and the board says *"Highest position reached. I cannot move up any further."*

#. Now take your hand **out of the frame** and leave it out for 3 seconds. The panel flips to **Ready — show a gesture**. That phrase is your green light: the app is armed again and the next gesture will count.

#. Repeat the same rhythm with the other three gestures — hold, wait for the action, then remove your hand. A **fist** tilts the camera down one 5° step (*"Moving down."*) until it stops at **110°**, the lowest position, where the speaker says *"Lowest position reached. I cannot move down any further."* An **open hand** sends the pan-tilt back to center, pan at 90° and tilt at 85° (*"Back to the center."*), and a **V-sign** saves a photo and says *"Photo taken."*

.. image:: img/06_ai_gesture_camera.png
   :width: 600
   :align: center

**How it Works**

The whole project is a pipeline with a filter in the middle: frames go in at the top, and at the bottom either a servo moves, a photo is written, or a sentence is spoken — never more than one of those per gesture. The filter is needed because the hand-gestures model runs on every frame and reports what it sees many times per second; if each report triggered an action, one thumbs up would slam the camera into its mechanical limit in a blink. Raw labels are not decisions — they are noise that has to be turned into **events**.

* ``06 AI Gesture Camera/`` — the app folder

  * Bricks

    * ``video_object_detection`` — the detection model, declared with ``model: hand-gestures`` in ``app.yaml``
    * ``web_ui`` — the Web UI server and socket channel
    * ``sunfounder_tts`` — online text-to-speech through the carrier's speaker

  * Sketch libraries

    * ``Arduino_HardwareServo (0.0.1)`` — hardware-PWM servo control, declared in ``sketch.yaml``

  * Files

    * ``assets/``

      * ``index.html`` — Web UI structure: camera feed, gesture card, hint line
      * ``app.js`` — Browser logic (Socket.IO client)
      * ``style.css`` — Visual styling
      * ``libs/`` — JavaScript libraries (Socket.IO)
      * ``img/`` — Static resources

    * ``python/``

      * ``main.py`` — Gesture state machine, photo capture, speech, and Bridge calls

    * ``sketch/``

      * ``sketch.yaml`` — Sketch configuration and library version
      * ``sketch.ino`` — Servo control on the microcontroller

    * ``README.md`` — Project documentation and usage guide
    * ``app.yaml`` — App metadata (name, icon, bricks used)

The data path from gesture to action:

.. mermaid::

   sequenceDiagram
       participant H as Your hand (camera)
       participant P as Python (main.py)
       participant S as Sketch (sketch.ino)
       participant B as Browser (Web UI)

       H->>P: frames → hand-gestures model (confidence ≥ 0.25)
       P->>P: best_gesture() → label + confidence
       P->>P: same label held for 0.6 s → lock gesture_armed
       P->>P: action_queue.put_nowait((label, confidence))
       P->>S: Bridge.call("tilt_up" / "tilt_down" / "center_pan_tilt")
       S->>S: step 5° within 60°–110°; pan and tilt back to center
       S-->>P: new tilt angle
       P->>P: take_photo() → camera.capture() → cv2.imwrite()
       P->>B: gesture_result: action + "remove your hand"
       P->>P: tts.say("Moving up.")
       P->>P: re-arm after 5 s and 3 s with no gesture
       P->>B: "Ready — show a gesture"

Here's what each component does:

**Python (main.py)** — runs on the Linux MPU
  * ``detection.on_detect_all(on_detections)`` receives every frame's detections; ``best_gesture()`` keeps the four labels of ``GESTURE_NAMES`` and ignores everything else
  * ``CONFIDENCE_THRESHOLD`` (0.25) decides how sure the model has to be before a label is even considered
  * ``on_detections()`` accepts a gesture only after the **same** label has held for ``STABLE_SECONDS`` (0.6) — a one-frame flicker restarts the clock instead of firing
  * An accepted gesture sets ``gesture_armed = False`` and queues the label, so one gesture earns exactly one action
  * ``rearm_after_hand_is_removed()`` unlocks only after ``MIN_ACTION_INTERVAL`` (5 s) **and** ``REARM_NO_GESTURE_SECONDS`` (3 s) with no recognizable gesture
  * ``action_queue`` is a ``queue.Queue(maxsize=1)`` filled with ``put_nowait()`` — at most one action can ever be waiting
  * ``action_worker()`` performs the slow work on a background thread: ``Bridge.call()`` for the servos, ``take_photo()`` for the JPEG, and ``tts.say()`` for the voice
  * ``camera.capture()`` grabs a fresh frame and ``cv2.imwrite()`` writes it as ``gesture_001.jpg``, ``gesture_002.jpg``, and so on, so no photo is ever overwritten
  * ``ui.send_message("gesture_result", ...)`` reports the gesture, its confidence, the action, and a timestamp to the page

**Sketch (sketch.ino)** — runs on the STM32 MCU
  * ``HardwareServo`` drives the pan servo on **D9** and the tilt servo on **D10** with hardware PWM
  * Keeps the only hardware state that matters, ``tiltAngle``, which starts at the ``TILT_CENTER_ANGLE`` of 85°
  * ``Bridge.provide("tilt_up", tiltUp)`` subtracts ``TILT_STEP`` (5°) and squeezes the result into the 60°–110° window with ``constrain()``, then returns the new angle
  * ``Bridge.provide("tilt_down", tiltDown)`` adds the same 5° step, clamped to the same window
  * ``Bridge.provide("center_pan_tilt", centerPanTilt)`` writes the pan servo back to 90°, waits 150 ms, then returns the tilt to 85° — the short delay keeps both servos from pulling current at the same instant
  * ``loop()`` does nothing but ``delay(10)`` — every movement arrives through the Bridge

**Bridge** — communication channel between MPU and MCU
  * Sketch side: ``Bridge.provide("name", function)`` exposes a function
  * Python side: ``Bridge.call("name", args...)`` invokes it and receives its return value
  * That return value is how Python knows the exact tilt angle to print and speak about

**Browser (index.html / app.js)** — runs in the user's browser
  * Shows the live camera feed from the ``web_ui`` brick, the current gesture, and its confidence
  * ``socket.on('gesture_result')`` writes the gesture name, the confidence percentage, and the action text, including the *"remove your hand"* reminder
  * The hint line lists the four moves: 👍 Move up · ✊ Move down · ✌️ Take photo · 🖐️ Center pan-tilt

3. Experiment
---------------

**Learn the Rhythm of the Lock**

Run the app and try each of these in order. The point is to feel the three timers — the 0.6 s hold, the 5 s lock, and the 3 s re-arm — rather than to memorize them:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - You do
     - Result
   * - Hold a thumbs up steady for about 0.6 seconds
     - The page shows **Thumbs up** with a confidence score, the camera tilts up 5° (85° → 80°), and the board says *"Moving up."*
   * - Keep holding that same thumbs up for another ten seconds
     - Nothing else happens — one gesture earns exactly one action, no matter how long the hand stays there
   * - Wave a gesture quickly past the lens and pull it away
     - Nothing fires — the label never survives the full 0.6-second window
   * - Lower your hand and keep it out of the frame for 3 seconds
     - The card flips to **Ready — show a gesture**, the Console prints ``[READY]``, and the app is armed again
   * - Show a fist, then a fist again, then a fist again
     - Each tilt-down is 5°: the camera walks 85° → 90° → 95° → 100° → 105° → 110°, one step per fist
   * - Keep showing a fist once the tilt has reached 110°
     - The camera does not move, and the board says *"Lowest position reached. I cannot move down any further."*
   * - Show a thumbs up five times in a row
     - Five 5° steps later the tilt sits at 60°; one more thumbs up changes nothing and the board says *"Highest position reached. I cannot move up any further."*
   * - Show an open hand
     - The pan returns to 90° and the tilt to 85° while the speaker says *"Back to the center."*
   * - Show a V-sign
     - A new ``gesture_NNN.jpg`` appears in ``/app/photos/`` and the board says *"Photo taken."*
   * - Change straight from a fist into a V-sign without removing your hand
     - The stable timer restarts on the new label, so neither action fires until you hold one of them still

**Challenge: Find the Edges of the Model**

The hand-gestures model was trained on clean, well-lit hands against simple backgrounds — your desk is none of those things. Move your hand closer and farther, and find the distance where a gesture stops being recognized at all. Try it with a cluttered background, with a bare wall, with a lamp aimed at your palm, and with the room lights off. Then try a gesture at an angle, or partially hidden behind a coffee mug. Watch the confidence percentage on the page as you go: at what point does it fall below the 25% threshold and the panel go quiet? Which of the four gestures is the most reliable for *your* hand, and which one do you have to hold longest? There is no right answer — the goal is to learn where this model's eyesight ends, because every gesture project you build later depends on that boundary.

**Challenge: Rework the Rhythm**

The three numbers at the top of ``main.py`` are a personality, not a law. Change ``STABLE_SECONDS`` to ``0.2`` and the app becomes twitchy — how many false triggers can you collect in a minute of casual hand movement? Raise it to ``2.0`` and it feels stubborn — how long does a deliberate gesture take to register, and does that change how carefully you pose your hand? Then shrink ``MIN_ACTION_INTERVAL`` to ``1.0`` and ``REARM_NO_GESTURE_SECONDS`` to ``1.0`` and try to chain four gestures as fast as you can. Which combination makes the app feel like a tool, and which makes it feel like it is arguing with you? Change one number at a time, run again, and describe the difference out loud before you touch the next one.

4. Troubleshooting
--------------------

**My hand is clearly in the frame but no gesture ever fires**

* **Cause:** The model cannot read the gesture, so ``best_gesture()`` keeps returning nothing and the stable window never even starts. Common reasons: the hand is too far away or too close, the background is busy, the lighting is dim, or part of the hand is outside the frame.
* **Solution:** Bring your hand to about 50 cm and fill a good part of the frame with it, use a plain light background, and keep your whole hand visible. Hold the pose steady rather than moving it. If the panel still never shows a gesture name, the model is not recognizing the pose at all — the Console only prints ``[GESTURE]`` lines for gestures that were actually accepted, so a completely silent Console means the recognition step is failing, not the state machine.

**The action fires twice, or fires again while my hand is still there**

* **Cause:** The app is only re-armed after **both** the 5-second action lock **and** 3 seconds with no recognizable gesture. If your hand never leaves the frame, ``last_detection_time`` keeps being refreshed and the app stays locked — so the next thing that happens can feel like a delayed repeat of the first action. Two genuine actions from one "gesture" usually mean the model saw two different labels: a fist that relaxes into an open hand is two gestures, not one.
* **Solution:** Treat removing your hand as part of the gesture. After each action, take your hand completely out of the frame and wait for **Ready — show a gesture** before presenting the next one. To confirm what really happened, read the Console: every accepted gesture prints exactly one ``[GESTURE]`` line with the label, the confidence, and the action. Two lines mean two gestures were recognized — and if you want more patience than that, raise ``MIN_ACTION_INTERVAL`` and ``REARM_NO_GESTURE_SECONDS`` at the top of ``main.py``.

**The camera moves but there is no sound**

* **Cause:** The TTS runtime is still being prepared, the UNO Q has no Internet connection, or the speech worker failed to start and printed a ``[TTS ERROR]`` line.
* **Solution:** Wait for ``[TTS] Ready.`` on the Console before expecting speech — the very first run can take half an hour to download dependencies, and EdgeTTS synthesizes its audio online, so the board must stay connected to the Internet. If you see a ``[TTS ERROR]`` line instead, re-run the app once the setup has finished. Volume is set to 40 in ``set_volume()``, so if the carrier is sitting next to a fan or a laptop speaker, move it somewhere quieter before assuming the audio is broken.

**The servo buzzes instead of moving, or the photo is missing from the folder**

* **Cause:** For the servos, the battery pack is not connected (USB power alone is too weak for two servos under load), the mechanism is mechanically obstructed, or the tilt has reached its 60°/110° limit and correctly refuses to move further. For the photo, ``camera.capture()`` returned nothing or ``cv2.imwrite()`` failed, so the worker reported ``Photo failed``.
* **Solution:** Connect the battery pack to the Robot Shield, check that the pan and tilt brackets swing freely by hand, and remember that the tilt stops at 60° and 110° by design — a servo that stops moving after one more thumbs up or fist is working correctly, and the board says "Highest position reached" or "Lowest position reached" when that happens. For a missing photo, look for the Console line: ``Photo saved: gesture_NNN.jpg`` confirms the exact filename, so browse ``/app/photos/`` for that file; if you see ``Photo failed`` instead, the camera was busy or not started, so stop the app and run it again.

5. Summary
-------------

You just taught your UNO Q to take orders from your hand — one wave of a thumbs up and a camera on your desk physically moves. That is a real robot control loop, and the interesting part is not the gesture model at all: it is the small state machine that decides *when* a gesture counts. Along the way you learned:

* How to run the ``VideoObjectDetection`` brick with the **hand-gestures** model and map its labels (``good``, ``neut``, ``five``, ``peace``) to real actions
* Why raw model output has to be filtered: a 0.6-second stable window turns a stream of flickering labels into single, deliberate events
* How a lock plus a re-arm rule — 5 seconds after an action, 3 seconds with no hand in view — guarantees one gesture produces exactly one action
* How a background worker and a one-slot queue keep slow work (servos, disk writes, online speech) out of the AI detection callback
* How the same sketch can expose several unrelated abilities — a 5° tilt step, a centering move — through the Bridge, and return an angle Python can report

The pattern you built here — detect something, decide whether it is real, then act — is the pattern behind almost every physical AI system. In the next project, the camera stops waiting for your hand and starts **following your face**: the pan-tilt will track you as you move around the room, and greet you when you arrive.
