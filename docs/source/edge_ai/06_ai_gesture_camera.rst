.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

06 AI Gesture Camera
====================

In the previous project, the AI counted what the camera saw — but the only thing that changed was a number on a page. Nothing in the room moved. This project hands over the controls: **your hand becomes the remote**. A thumbs up tilts the camera up, a fist tilts it down, an open hand sends the pan-tilt back to center, and a V-sign takes a photo. Every gesture also flashes the status LED and answers you out loud — *"Moving up."*, *"Photo taken."* — so you always know the board understood. The real lesson, though, is not the gestures. It is teaching the UNO Q to tell a **deliberate gesture** apart from a hand that simply happens to be in front of the lens.

.. image:: img/06_ai_gesture_camera.png
   :width: 600
   :align: center

In this lesson, you will learn to:

* Run the ``VideoObjectDetection`` brick with its **hand-gestures** model and read the labels it produces
* Turn one gesture into one physical action: a 15° tilt step, a centering move, a photo, or a spoken reply
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
   * - 1 * :ref:`cpn_led` (Red)
     - 1 * :ref:`cpn_resistor` (220Ω)
   * - |list_red_led|
     - |list_220ohm|

.. note::

   Before using the camera, make sure external carriers are enabled on your UNO Q — this is a one-time setup: :ref:`enable_external_carriers`.

**Wiring Diagram**

Wire the LED between **D5** and **GND** with the 220 Ω resistor in series — the same small circuit you built for the very first LED project, and it needs no breadboard rows beyond that one loop. Then plug the pan servo's signal lead into **D9** and the tilt servo's into **D10**, and make sure both servos are powered from the Robot Shield's **5 V** and **GND** servo headers, because two servos moving under load draw far more current than a signal pin could ever supply.

2. Code
---------

**Import the Code**

#. Open **Arduino App Lab**, go to **Apps**. Click the dropdown arrow next to **Create new app +** and select **Import App**.

   .. image:: /img/app_import_app.png
      :width: 600
      :align: center

#. Select **Import from Computer**.

   .. image:: /img/app_import_pc.png
      :width: 600
      :align: center

#. Navigate to the ``unoq-ai-kit/edge_ai/`` folder and select ``06 AI Gesture Camera.zip``.

#. The app appears in **Apps** — click it to open.

**Run the Code**

#. The servos and the camera together draw more power than the USB port alone can provide, so connect the battery pack to the Robot Shield.

#. Click the **Run** button (▶). The pan-tilt swings to its center position, the LED blinks once, and the Console prints ``AI Gesture Camera is running.``

#. While the speech engine prepares itself, the Console prints ``[TTS] Ready.``

   .. note::

      The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

#. Open the **Web UI** tab. The live camera feed fills the card, the gesture panel reads **Current Gesture: Waiting...** with no confidence yet, and the hint line reminds you of the four moves: 👍 Move up · ✊ Move down · ✌️ Take photo · 🖐️ Center pan-tilt.

#. Hold up a **thumbs up**, roughly 50 cm from the camera, with your whole hand inside the frame and a plain background behind it. Keep it steady for about 0.6 seconds. The panel switches to **Thumbs up** with a confidence percentage, the tilt servo lifts the camera 15°, the LED flashes, the speaker says *"Moving up."*, and the last-action line adds *"— remove your hand"*.

#. Now take your hand **out of the frame** and leave it out for 3 seconds. The panel flips to **Ready — show a gesture**. That phrase is your green light: the app is armed again and the next gesture will count.

#. Repeat the same rhythm with the other three gestures — hold, wait for the action, then remove your hand. A **fist** tilts the camera down 15° (*"Moving down."*), an **open hand** sends the pan-tilt back to center (*"Back to the center."*), and a **V-sign** saves a photo and says *"Photo taken."*

.. image:: img/06_ai_gesture_camera.png
   :width: 600
   :align: center

**The Code**

Two files run on two different processors:

* ``python/main.py`` — runs on the Linux MPU: the hand-gesture model, the gesture state machine, the photo, and the speech
* ``sketch/sketch.ino`` — runs on the STM32 MCU: the LED on D5 and the two servos on D9 and D10

**Python (main.py)** — runs on the Linux MPU

.. code-block:: python
   :linenos:

   """AI Gesture Camera — control camera tilt and take photos with gestures."""

   from datetime import UTC, datetime
   import os
   import queue
   import threading
   import time
   from pathlib import Path

   import cv2

   from arduino.app_utils import App, Bridge
   from arduino.app_bricks.video_objectdetection import VideoObjectDetection
   from arduino.app_bricks.web_ui import WebUI
   from arduino.app_peripherals.camera import Camera
   from sunfounder_tts import EdgeTTS


   CONFIDENCE_THRESHOLD = 0.25
   STABLE_SECONDS = 0.6
   MIN_ACTION_INTERVAL = 5.0
   REARM_NO_GESTURE_SECONDS = 3.0
   FLIP_IMAGE = True

   GESTURE_NAMES = {
       "good": "Thumbs up",
       "neut": "Fist",
       "five": "Open hand",
       "peace": "V-sign",
   }

   ui = WebUI()
   state_lock = threading.Lock()
   action_queue = queue.Queue(maxsize=1)

   gesture_armed = True
   candidate_gesture = None
   candidate_since = 0.0
   last_detection_time = 0.0
   last_action_time = 0.0

   photo_dir = Path("/app/photos")
   photo_dir.mkdir(parents=True, exist_ok=True)


   def send_result(label, confidence, action):
       ui.send_message("gesture_result", {
           "gesture": GESTURE_NAMES.get(label, "None"),
           "confidence": round(confidence * 100),
           "action": action,
           "timestamp": datetime.now(UTC).isoformat(),
       })


   def best_gesture(detections):
       best_label = None
       best_confidence = 0.0

       for label, instances in detections.items():
           if label not in GESTURE_NAMES:
               continue

           for instance in instances:
               confidence = float(instance.get("confidence", 0.0))
               if confidence > 1:
                   confidence /= 100
               if confidence > best_confidence:
                   best_label = label
                   best_confidence = confidence

       if best_confidence < CONFIDENCE_THRESHOLD:
           return None, 0.0
       return best_label, best_confidence


   def next_photo_path():
       index = 1
       while True:
           path = photo_dir / f"gesture_{index:03d}.jpg"
           if not path.exists():
               return path
           index += 1


   def take_photo():
       """Capture one frame without performing the operation in the AI callback."""
       frame = camera.capture()
       if frame is None:
           return None

       # Camera adjustments already rotate the image used by the model and preview.
       path = next_photo_path()
       if cv2.imwrite(str(path), frame):
           return path.name
       return None


   def action_worker():
       """Run hardware, photo, and TTS actions sequentially in one worker."""
       os.makedirs("/app/audio_output", exist_ok=True)

       try:
           tts = EdgeTTS()
           tts.set_voice("en-US-JennyNeural")
           tts.set_volume(40)
           print("[TTS] Ready.", flush=True)
       except Exception as error:
           tts = None
           print(f"[TTS ERROR] {type(error).__name__}: {error}", flush=True)

       while True:
           label, confidence = action_queue.get()

           try:
               if label == "good":
                   angle = Bridge.call("tilt_up", "")
                   action = f"Camera moved up to {angle} degrees"
                   speech = "Moving up."
               elif label == "neut":
                   angle = Bridge.call("tilt_down", "")
                   action = f"Camera moved down to {angle} degrees"
                   speech = "Moving down."
               elif label == "five":
                   Bridge.call("center_pan_tilt", "")
                   action = "Pan-tilt centered"
                   speech = "Back to the center."
               else:
                   photo_name = take_photo()
                   if photo_name:
                       action = f"Photo saved: {photo_name}"
                       speech = "Photo taken."
                   else:
                       action = "Photo failed"
                       speech = "I could not take the photo."

               Bridge.call("flash_led", "")

               print(
                   f"[GESTURE] {GESTURE_NAMES[label]} — "
                   f"{confidence * 100:.0f}% — {action}",
                   flush=True,
               )
               send_result(label, confidence, f"{action} — remove your hand")

               if tts is not None:
                   try:
                       tts.say(speech)
                   except Exception as error:
                       print(f"[TTS ERROR] {type(error).__name__}: {error}", flush=True)

           except Exception as error:
               print(f"[ACTION ERROR] {type(error).__name__}: {error}", flush=True)
               send_result(label, confidence, "Action failed")
           finally:
               action_queue.task_done()


   def on_detections(detections):
       """Require one stable gesture, then lock until the hand is removed."""
       global gesture_armed, candidate_gesture, candidate_since
       global last_detection_time, last_action_time

       label, confidence = best_gesture(detections)
       if label is None:
           return

       now = time.monotonic()

       with state_lock:
           last_detection_time = now

           if not gesture_armed or now - last_action_time < MIN_ACTION_INTERVAL:
               return

           if label != candidate_gesture:
               candidate_gesture = label
               candidate_since = now
               return

           if now - candidate_since < STABLE_SECONDS:
               return

           gesture_armed = False
           candidate_gesture = None
           last_action_time = now

       try:
           action_queue.put_nowait((label, confidence))
       except queue.Full:
           print("[BUSY] Previous gesture action is still running.", flush=True)


   def rearm_after_hand_is_removed():
       """Unlock only after a minimum delay and three seconds with no gesture."""
       global gesture_armed, candidate_gesture

       while True:
           should_rearm = False
           now = time.monotonic()

           with state_lock:
               if (
                   not gesture_armed
                   and now - last_action_time >= MIN_ACTION_INTERVAL
                   and now - last_detection_time >= REARM_NO_GESTURE_SECONDS
               ):
                   gesture_armed = True
                   candidate_gesture = None
                   should_rearm = True

           if should_rearm:
               print("[READY] Show the next gesture.", flush=True)
               send_result("", 0.0, "Ready — show a gesture")

           time.sleep(0.2)


   if FLIP_IMAGE:
       camera = Camera(adjustments=lambda frame: frame[::-1, :])
   else:
       camera = Camera()

   camera.start()

   detection = VideoObjectDetection(
       camera,
       confidence=CONFIDENCE_THRESHOLD,
       debounce_sec=0.2,
   )
   detection.on_detect_all(on_detections)

   threading.Thread(target=action_worker, daemon=True).start()
   threading.Thread(target=rearm_after_hand_is_removed, daemon=True).start()

   print("AI Gesture Camera is running.", flush=True)
   App.run()

**Sketch (sketch.ino)** — runs on the STM32 MCU

.. code-block:: cpp
   :linenos:

   /*
    * AI Gesture Camera
    *
    * LED: D5 through a 220 ohm resistor
    * Pan servo: D9
    * Tilt servo: D10
    */

   #include <Arduino_RouterBridge.h>
   #include <Arduino_HardwareServo.h>

   const int LED_PIN = 5;
   const int PAN_SERVO_PIN = 9;
   const int TILT_SERVO_PIN = 10;

   const int PAN_CENTER_ANGLE = 90;
   const int TILT_CENTER_ANGLE = 85;
   const int TILT_MIN_ANGLE = 60;
   const int TILT_MAX_ANGLE = 110;
   const int TILT_STEP = 15;

   HardwareServo panServo;
   HardwareServo tiltServo;
   int tiltAngle = TILT_CENTER_ANGLE;


   int flashLed(String dummy)
   {
       (void)dummy;
       digitalWrite(LED_PIN, HIGH);
       delay(120);
       digitalWrite(LED_PIN, LOW);
       return 1;
   }


   int tiltUp(String dummy)
   {
       (void)dummy;
       tiltAngle = constrain(tiltAngle - TILT_STEP, TILT_MIN_ANGLE, TILT_MAX_ANGLE);
       tiltServo.write(tiltAngle);
       return tiltAngle;
   }


   int tiltDown(String dummy)
   {
       (void)dummy;
       tiltAngle = constrain(tiltAngle + TILT_STEP, TILT_MIN_ANGLE, TILT_MAX_ANGLE);
       tiltServo.write(tiltAngle);
       return tiltAngle;
   }


   int centerPanTilt(String dummy)
   {
       (void)dummy;
       panServo.write(PAN_CENTER_ANGLE);
       delay(150);
       tiltAngle = TILT_CENTER_ANGLE;
       tiltServo.write(tiltAngle);
       return 1;
   }


   void setup()
   {
       pinMode(LED_PIN, OUTPUT);
       digitalWrite(LED_PIN, LOW);

       panServo.attach(PAN_SERVO_PIN);
       tiltServo.attach(TILT_SERVO_PIN);
       panServo.write(PAN_CENTER_ANGLE);
       delay(150);
       tiltServo.write(TILT_CENTER_ANGLE);

       Bridge.begin();
       Bridge.provide("flash_led", flashLed);
       Bridge.provide("tilt_up", tiltUp);
       Bridge.provide("tilt_down", tiltDown);
       Bridge.provide("center_pan_tilt", centerPanTilt);
   }


   void loop()
   {
       delay(10);
   }

**How it Works**

The whole project is a pipeline with a filter in the middle: frames go in at the top, and at the bottom either a servo moves, a photo is written, or a sentence is spoken — never more than one of those per gesture.

.. mermaid::

   sequenceDiagram
       participant H as Your hand (camera)
       participant P as Python (main.py)
       participant S as Sketch (sketch.ino)
       participant W as Browser (Web UI)

       H->>P: frames → hand-gestures model (confidence ≥ 0.25)
       P->>P: best_gesture() → label + confidence
       P->>P: same label held for 0.6 s? (candidate_since)
       P->>P: lock: gesture_armed = False, last_action_time = now
       P->>P: action_queue.put_nowait((label, confidence))
       P->>S: Bridge.call("tilt_up" / "tilt_down" / "center_pan_tilt")
       S->>S: constrain 60°–110°, step 15°; pan back to 90°
       P->>S: Bridge.call("flash_led")
       S->>S: D5 HIGH for 120 ms
       P->>P: take_photo() → camera.capture() → cv2.imwrite(gesture_NNN.jpg)
       P->>W: gesture_result: action + "remove your hand"
       P->>P: tts.say("Moving up.")
       P->>P: re-arm thread: 5 s since action AND 3 s with no gesture
       P-->>W: "Ready — show a gesture"

**The problem: the model is far too eager** — The hand-gestures model runs on every camera frame and reports what it sees many times per second, and ``debounce_sec=0.2`` only limits repeats to about five per second. If each report triggered an action, a single thumbs up would fire the tilt over and over and the camera would slam into its limit in a blink. The labels also flicker — for one or two frames a fist can read as an open hand, or a hand at the edge of the frame can read as nothing at all. Raw labels are therefore not decisions; they are noise that has to be filtered into **events**.

**The stable window** — Every accepted action starts life as a *candidate*. ``on_detections()`` compares the new label with ``candidate_gesture``: if they differ, it records the new label, resets ``candidate_since`` to the current time, and returns without doing anything. Only when the **same** label keeps arriving for ``STABLE_SECONDS = 0.6`` seconds does the gesture count as deliberate. A one-frame flicker therefore dies harmlessly, because the very next different label restarts the clock. You can feel this rule while you use the app: a quick wave past the lens does nothing, while a hand held still for a beat gets an immediate reaction.

**Lock, then re-arm** — When a gesture survives the window, the state machine does three things at once: it sets ``gesture_armed = False`` so no further action can be accepted, clears the candidate, and stamps ``last_action_time``. A background thread, ``rearm_after_hand_is_removed()``, wakes every 0.2 seconds and unlocks only when **both** of these are true: at least ``MIN_ACTION_INTERVAL = 5.0`` seconds have passed since the action, **and** at least ``REARM_NO_GESTURE_SECONDS = 3.0`` seconds have passed since a gesture was last seen. Because ``last_detection_time`` is only refreshed when the model reports a *recognizable* gesture, that second condition is really asking "is your hand gone?" When the lock finally lifts, Python prints ``[READY] Show the next gesture.`` and sends *Ready — show a gesture* to the page. Requiring the hand to leave is not just fussiness: it guarantees each action is a separate, intentional act, and it gives the servo five quiet seconds to finish moving before the next command can arrive.

**The action queue keeps detection responsive** — The detection callback has to return fast, because while it runs no new frame is being analyzed. Everything slow lives elsewhere: ``action_worker()`` is a separate thread that owns the Bridge calls, the JPEG write, and the speech. ``on_detections()`` only packs ``(label, confidence)`` into ``action_queue`` — a ``queue.Queue(maxsize=1)`` — using ``put_nowait()``. A maximum size of one is deliberate: at most one action can ever be waiting, so a flurry of gestures cannot pile up and make the camera act out something you did ten seconds ago. If the worker is still busy, the queue is full, Python prints ``[BUSY] Previous gesture action is still running.``, and the new gesture is simply dropped. Servo moves, photos, and speech all happen in the same thread, one after another, so they can never collide.

**Why speech lives in a background worker** — ``tts.say()`` is the slowest thing in the project: EdgeTTS sends the sentence to an online service and waits for the audio to come back, which takes a noticeable moment. Run inside the detection callback, it would freeze the camera on every gesture and leave the Web UI stale. Instead, the ``EdgeTTS`` object is created once when the worker starts and reused for the life of the app, and each sentence is spoken at the **end** of the worker's cycle — after the servo, the LED, the photo, and the UI update are already done. That ordering is why the camera reacts the instant your gesture lands while the voice arrives half a beat later, and why the AI loop never notices that speech is happening at all.

**On the servo side** — The sketch holds the only state the hardware cares about: ``tiltAngle``, which starts at ``TILT_CENTER_ANGLE = 85``. ``tilt_up`` subtracts 15° and ``tilt_down`` adds 15°, and each result is squeezed by ``constrain()`` into the 60°–110° window, so the bracket can never be driven into its own mount: from center you get two steps up (85 → 70 → 60) and two steps down (85 → 100 → 110), and after that the servo simply stops where it is. ``center_pan_tilt`` writes the pan servo to ``PAN_CENTER_ANGLE = 90``, waits 150 ms for it to arrive, then returns the tilt to 85 — the short delay keeps both servos from pulling current at the same instant. ``flash_led`` is the simplest function in the file: D5 HIGH, 120 ms, LOW, a visible receipt that the gesture landed. Note that on this bracket a *smaller* tilt angle points the camera *up* — the camera module sits upside down on the carrier, which is also why ``FLIP_IMAGE = True`` flips every frame before the model and the preview see it. If your assembled bracket has the servo the other way round, swap the ``+`` and ``-`` in ``tilt_up`` and ``tilt_down``.

**On the photo side** — ``take_photo()`` calls ``camera.capture()`` directly instead of reusing a frame the model has already handled, so the file it saves is a clean, full-size image. ``next_photo_path()`` then counts upward from ``gesture_001.jpg`` and stops at the first name that does not exist yet, so nothing is ever overwritten — your two-hundredth photo becomes ``gesture_200.jpg`` rather than replacing an earlier one. ``cv2.imwrite()`` writes the JPEG and returns ``True`` on success; if the capture or the write fails, the worker reports ``Photo failed`` and speaks *"I could not take the photo."* instead of failing silently. Every step of the way the page stays in the loop: ``send_result()`` pushes the gesture name, its confidence as a percentage, the action text, and a timestamp over the ``gesture_result`` socket event, and the Web UI prints them in the gesture card.

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
     - The page shows **Thumbs up** with a confidence score, the camera tilts up 15°, the LED flashes, and the board says *"Moving up."*
   * - Keep holding that same thumbs up for another ten seconds
     - Nothing else happens — one gesture earns exactly one action, no matter how long the hand stays there
   * - Wave a gesture quickly past the lens and pull it away
     - Nothing fires — the label never survives the full 0.6-second window
   * - Lower your hand and keep it out of the frame for 3 seconds
     - The card flips to **Ready — show a gesture**, the Console prints ``[READY]``, and the app is armed again
   * - Show a fist, then a fist again, then a fist again
     - Each tilt-down is 15°: the camera walks 85° → 100° → 110° and then refuses to go further
   * - Show an open hand
     - The pan returns to 90° and the tilt to 85° while the speaker says *"Back to the center."*
   * - Show a V-sign
     - The LED flashes, the board says *"Photo taken."*, and a new ``gesture_NNN.jpg`` appears in ``/app/photos/``
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

**The camera moves and the LED flashes, but there is no sound**

* **Cause:** The TTS runtime is still being prepared, the UNO Q has no Internet connection, or the speech worker failed to start and printed a ``[TTS ERROR]`` line.
* **Solution:** Wait for ``[TTS] Ready.`` on the Console before expecting speech — the very first run can take half an hour to download dependencies, and EdgeTTS synthesizes its audio online, so the board must stay connected to the Internet. If you see a ``[TTS ERROR]`` line instead, re-run the app once the setup has finished. Volume is set to 40 in ``set_volume()``, so if the carrier is sitting next to a fan or a laptop speaker, move it somewhere quieter before assuming the audio is broken.

**The servo buzzes instead of moving, or the photo is missing from the folder**

* **Cause:** For the servos, the battery pack is not connected (USB power alone is too weak for two servos under load), the mechanism is mechanically obstructed, or the tilt has reached its 60°/110° limit and correctly refuses to move further. For the photo, ``camera.capture()`` returned nothing or ``cv2.imwrite()`` failed, so the worker reported ``Photo failed``.
* **Solution:** Connect the battery pack to the Robot Shield, check that the pan and tilt brackets swing freely by hand, and remember that the tilt stops at 60° and 110° by design — a servo that stops moving after two gestures in the same direction is working correctly. For a missing photo, look for the Console line: ``Photo saved: gesture_NNN.jpg`` confirms the exact filename, so browse ``/app/photos/`` for that file; if you see ``Photo failed`` instead, the camera was busy or not started, so stop the app and run it again.

5. Summary
-------------

You just taught your UNO Q to take orders from your hand — one wave of a thumbs up and a camera on your desk physically moves. That is a real robot control loop, and the interesting part is not the gesture model at all: it is the small state machine that decides *when* a gesture counts. Along the way you learned:

* How to run the ``VideoObjectDetection`` brick with the **hand-gestures** model and map its labels (``good``, ``neut``, ``five``, ``peace``) to real actions
* Why raw model output has to be filtered: a 0.6-second stable window turns a stream of flickering labels into single, deliberate events
* How a lock plus a re-arm rule — 5 seconds after an action, 3 seconds with no hand in view — guarantees one gesture produces exactly one action
* How a background worker and a one-slot queue keep slow work (servos, disk writes, online speech) out of the AI detection callback
* How the same sketch can expose several unrelated abilities — an LED flash, a tilt step, a centering move — through the Bridge, and return a value Python can report

The pattern you built here — detect something, decide whether it is real, then act — is the pattern behind almost every physical AI system. In the next project, the camera stops waiting for your hand and starts **following your face**: the pan-tilt will track you as you move around the room, and greet you when you arrive.
