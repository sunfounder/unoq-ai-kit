.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

07 Face Tracking Camera
=======================

The gesture camera moved, but only in fixed steps: one gesture, one 15° nudge, then it waited for you to leave the frame. What if the camera could *keep its eyes on you* instead? In this lesson, the UNO Q not only detects your face — it **follows it**. The pan-tilt camera greets you, then tracks you as you move left, right, up, and down, like a tiny robot that wants to keep you in the center of its view.

In this lesson, you will learn to:

* Greet a face **once per visit** with spoken text ("Nice to meet you.")
* Track a face with a **pan-tilt camera** that moves in both directions
* Use a **dead zone** to prevent servo jitter from tiny movements
* Automatically return the camera to center when the face is lost
* Coordinate the Linux MPU (AI + speech) and the STM32 MCU (servos) through Bridge

1. Setup
----------

**What You Need**

.. list-table::
   :widths: 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * USB Cable
   * - |list_pan_tilt|
     - |list_usb_cable|

**Software Requirements**

This project uses the following Bricks and sketch library:

* Bricks (declared in ``app.yaml``):
  * ``video_object_detection`` — runs the **face-detection** AI model on every camera frame
  * ``web_ui`` — serves the Web UI with the live camera feed and face status
  * ``sunfounder_tts`` — text-to-speech for the greeting (EdgeTTS)
* Libraries (declared in ``sketch.yaml``):
  * ``Arduino_HardwareServo`` (0.0.1) — drives the servos with hardware PWM

.. note::

   Before using the camera, make sure external carriers are enabled on your UNO Q — this is a one-time setup: :ref:`enable_external_carriers`.

.. note::

   The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

**Wiring Diagram**

This lesson uses no breadboard components — everything plugs into the Robot Shield. Plug the pan servo into pin **D9** and the tilt servo into pin **D10** on the Robot Shield's servo headers.

.. image:: /img/wiring/wiring_imu_servo.png
   :width: 600
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

#. Navigate to the ``unoq-ai-kit/edge_ai/`` folder and select ``07 Face Tracking Camera.zip``.

#. The app appears in **Apps** — click it to open.

**Run the Code**

#. The pan-tilt servos draw more power than the USB port alone can provide, so connect the battery pack to the Robot Shield.

#. Click the **Run** button (▶). The servos move to the 90° center position. On the Console you'll see the Python side announce itself: ``Face Tracking Camera with TTS is running.``, and once the speech engine is ready, ``EdgeTTS ready.`` The sketch prints its own banner, ``=== Face Tracking Camera ===``, over the serial connection.

#. Open the **Web UI** tab. The live camera feed fills the page, and a status area reports **Looking for a face** — "The pan-tilt is centered and waiting."

#. Stand in front of the camera. The board greets you with *"Nice to meet you."* and the status flips to **Face detected** — "The pan and tilt servos are following the face."

#. Move left and right, then duck and rise. The camera follows you to keep your face centered. Now step out of view and count to three — after about 2.5 seconds the camera returns to center, the status goes back to **Looking for a face**, and the next face that appears triggers a fresh greeting.

.. image:: img/07_face_tracking_camera.png
   :width: 600
   :align: center

**The Code**

The project has two files that run on two different processors:

* ``sketch/sketch.ino`` — runs on the STM32 MCU and physically moves the servos
* ``python/main.py`` — runs on the Linux MPU: face detection, greeting speech, and the tracking decisions

.. code-block:: cpp
   :linenos:

   /*
    * Face Tracking Camera
    *
    * The pan servo on D9 follows the detected face left and right.
    * The tilt servo on D10 follows the detected face up and down.
    * When the Linux application reports that the face is lost,
    * the pan-tilt returns to the center.
    */

   #include <Arduino_RouterBridge.h>
   #include <Arduino_HardwareServo.h>

   const int PAN_SERVO_PIN = 9;
   const int TILT_SERVO_PIN = 10;

   // Absolute servo angles — the center is 90°.
   const int PAN_MIN_ANGLE = 45;
   const int PAN_MAX_ANGLE = 135;
   const int TILT_MIN_ANGLE = 45;
   const int TILT_MAX_ANGLE = 115;
   const int CENTER_ANGLE = 90;

   const int STEP_DEGREES = 1;

   HardwareServo panServo;
   HardwareServo tiltServo;

   int panAngle = CENTER_ANGLE;
   int tiltAngle = CENTER_ANGLE;

   int panStep(int direction)
   {
       // direction > 0: face is right of center, turn right.
       panAngle += (direction > 0 ? STEP_DEGREES : -STEP_DEGREES);
       panAngle = constrain(panAngle, PAN_MIN_ANGLE, PAN_MAX_ANGLE);

       panServo.write(panAngle);
       return panAngle;
   }

   int tiltStep(int direction)
   {
       // direction > 0: face is below center, tilt the camera down.
       tiltAngle += (direction > 0 ? STEP_DEGREES : -STEP_DEGREES);
       tiltAngle = constrain(tiltAngle, TILT_MIN_ANGLE, TILT_MAX_ANGLE);

       tiltServo.write(tiltAngle);
       return tiltAngle;
   }

   int centerPanTilt(String dummy)
   {
       (void)dummy;

       panAngle = CENTER_ANGLE;
       tiltAngle = CENTER_ANGLE;

       panServo.write(CENTER_ANGLE);
       tiltServo.write(CENTER_ANGLE);
       return CENTER_ANGLE;
   }

   void setup()
   {
       Serial.begin(115200);

       panServo.attach(PAN_SERVO_PIN);
       tiltServo.attach(TILT_SERVO_PIN);

       panServo.write(CENTER_ANGLE);
       tiltServo.write(CENTER_ANGLE);
       delay(500);

       Bridge.begin();

       Bridge.provide("pan_step", panStep);
       Bridge.provide("tilt_step", tiltStep);
       Bridge.provide("center_pan_tilt", centerPanTilt);

       Serial.println("=== Face Tracking Camera ===");
   }

   void loop()
   {
       delay(20);
   }


.. code-block:: python
   :linenos:

   # SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
   #
   # SPDX-License-Identifier: MPL-2.0

   """
   Face Tracking Camera with Online TTS

   When a face is detected for the first time, the board greets
   "Nice to meet you." and starts following the face. The pan and tilt
   servos move to keep the face centered in the frame.

   When the face disappears for 2.5 seconds, the pan-tilt returns to
   the center and the next face triggers a new greeting.

   The greeting uses EdgeTTS:
   - Internet access is required.
   - No API key is required.
   """

   from datetime import UTC, datetime
   import queue
   import threading
   import time

   from arduino.app_utils import App, Bridge
   from arduino.app_bricks.web_ui import WebUI
   from arduino.app_bricks.video_objectdetection import VideoObjectDetection
   from arduino.app_peripherals.camera import Camera
   from sunfounder_tts import EdgeTTS


   # Custom web interface
   ui = WebUI()

   # CSI camera
   camera = Camera(adjustments=lambda frame: frame[::-1, :])
   camera.start()

   # Face detection
   detection = VideoObjectDetection(
       camera,
       confidence=0.5,
       debounce_sec=0.1,
   )

   # ── Tracking configuration ────────────────────────────────
   FRAME_WIDTH = 640
   FRAME_HEIGHT = 480
   DEAD_ZONE_RATIO = 0.10   # Ignore small offsets to reduce servo jitter.
   FACE_LOST_TIMEOUT = 2.5  # Seconds before returning to the center.

   # ── Greeting configuration ────────────────────────────────
   GREETING_TEXT = "Nice to meet you."
   GREETING_VOICE = "en-US-JennyNeural"
   GREETING_VOLUME = 50

   # ── Tracking state ────────────────────────────────────────
   face_visible = False
   last_face_time = 0.0
   state_lock = threading.Lock()

   # TTS runs in a background worker so tracking stays responsive
   speech_queue = queue.Queue()


   def speech_worker():
       """Play queued messages through EdgeTTS."""
       try:
           tts = EdgeTTS()
           tts.set_voice(GREETING_VOICE)
           tts.set_volume(GREETING_VOLUME)

           print("EdgeTTS ready.")

           while True:
               text = speech_queue.get()

               try:
                   tts.say(text)
               except Exception as error:
                   print(f"TTS error: {type(error).__name__}: {error}")
               finally:
                   speech_queue.task_done()

       except Exception as error:
           print(f"TTS startup failed: {type(error).__name__}: {error}")


   def speak(text):
       """Queue a message for speech without blocking tracking."""
       if text:
           speech_queue.put(str(text))


   def box_center(instance):
       """Return the (x, y) center of a detection box, or None.

       App Lab normally reports ``bounding_box_xyxy`` as the top-left
       and bottom-right coordinates. Older alternative formats are kept
       as fallbacks.
       """
       bbox_xyxy = instance.get("bounding_box_xyxy")

       if isinstance(bbox_xyxy, (list, tuple)) and len(bbox_xyxy) >= 4:
           x1, y1, x2, y2 = bbox_xyxy[:4]
           return (x1 + x2) / 2.0, (y1 + y2) / 2.0

       bbox = instance.get("bbox") or instance.get("box")

       if isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
           x, y, w, h = bbox[0], bbox[1], bbox[2], bbox[3]
       elif all(key in instance for key in ("x", "y", "width", "height")):
           x = instance["x"]
           y = instance["y"]
           w = instance["width"]
           h = instance["height"]
       else:
           return None

       if x + w <= 1.0 and y + h <= 1.0:
           # Normalized coordinates → scale to pixels.
           x, w = x * FRAME_WIDTH, w * FRAME_WIDTH
           y, h = y * FRAME_HEIGHT, h * FRAME_HEIGHT

       return x + w / 2.0, y + h / 2.0


   def as_detection_list(value):
       """Normalize one detection dictionary or a list of dictionaries."""
       if isinstance(value, dict):
           return [value]

       if isinstance(value, (list, tuple)):
           return [item for item in value if isinstance(item, dict)]

       return []


   def track_face(center_x, center_y):
       """Move both servos when the face drifts outside the dead zone."""
       offset_x = center_x - FRAME_WIDTH / 2.0
       offset_y = center_y - FRAME_HEIGHT / 2.0

       pan_direction = 0
       tilt_direction = 0

       if abs(offset_x) >= FRAME_WIDTH * DEAD_ZONE_RATIO:
           pan_direction = 1 if offset_x > 0 else -1

       if abs(offset_y) >= FRAME_HEIGHT * DEAD_ZONE_RATIO:
           tilt_direction = 1 if offset_y > 0 else -1

       if pan_direction:
           Bridge.call("pan_step", pan_direction)

       if tilt_direction:
           Bridge.call("tilt_step", tilt_direction)


   def send_detections(detections: dict):
       """Follow the most confident face in the current frame."""
       global face_visible, last_face_time

       best_center = None
       best_confidence = 0.0

       for instance in as_detection_list(detections.get("face")):
           confidence = float(instance.get("confidence", 0.0))

           if confidence > best_confidence:
               best_center = box_center(instance)
               best_confidence = confidence

       if best_confidence <= 0:
           return

       is_new_face = False

       with state_lock:
           last_face_time = time.monotonic()

           if not face_visible:
               # Face reappeared → greet again and start following.
               face_visible = True
               is_new_face = True

       if is_new_face:
           speak(GREETING_TEXT)

           ui.send_message("face_status", {
               "detected": True,
               "text": "Nice to meet you!",
               "timestamp": datetime.now(UTC).isoformat(),
           })

       # Greeting and status still work even if a future detector version
       # changes its bounding-box format.
       if best_center is not None:
           track_face(*best_center)


   def monitor_face_status():
       """Return the pan-tilt to center when the face has been lost."""
       global face_visible

       while True:
           should_center = False

           with state_lock:
               if face_visible:
                   elapsed = time.monotonic() - last_face_time

                   if elapsed >= FACE_LOST_TIMEOUT:
                       face_visible = False
                       should_center = True

           if should_center:
               Bridge.call("center_pan_tilt", "")

               ui.send_message("face_status", {
                   "detected": False,
                   "text": "Looking for a face",
                   "timestamp": datetime.now(UTC).isoformat(),
               })

           time.sleep(0.2)


   detection.on_detect_all(send_detections)

   threading.Thread(target=speech_worker, daemon=True).start()
   threading.Thread(target=monitor_face_status, daemon=True).start()

   print("Face Tracking Camera with TTS is running.")

   App.run()


**How it Works**

.. code-block:: text

   Camera (CSI, flipped vertically)
       │  every frame
       ▼
   VideoObjectDetection brick (face-detection model, confidence > 0.5)
       │
       ▼
   send_detections() → picks the most confident face in the frame
       │
       ├── first sighting of this visit?
       │       ├── speak "Nice to meet you."   (EdgeTTS, background thread)
       │       └── Web UI: "Face detected"
       │
       └── track_face() → compare face center with frame center
               ├── offset outside the 10% dead zone?
               │       └── Bridge.call("pan_step" / "tilt_step", ±1)
               └── sketch moves that servo 1° (pan 45–135°, tilt 45–115°)

   Background monitor thread (checks every 0.2 s)
       └── face gone for 2.5 s?
               ├── Bridge.call("center_pan_tilt") → both servos back to 90°
               └── Web UI: "Looking for a face"

**Face detection on the Linux MPU** — The ``VideoObjectDetection`` brick runs the same **face-detection** model you used earlier, frame after frame, right on the UNO Q. Each detection comes with a bounding box and a confidence score, and only detections above 0.5 confidence are accepted. The camera image is flipped vertically before analysis — on this carrier the camera is mounted upside down, so the flip makes the world look right side up again.

**Pick the best face** — When several faces are in view, ``send_detections()`` keeps only the most confident one. The bounding box is converted to a pixel coordinate at its center (handled by ``box_center()``), and that single point drives the tracking. The AI doesn't decide where to point the camera — it just reports where the face is, in numbers.

**Greeting once per visit** — The greeting isn't triggered by every detection, or the board would chatter nonstop. A Python-side flag, ``face_visible``, remembers whether a face is already being followed. Only when the flag flips from *lost* to *found* — the first time a face appears — does ``speak("Nice to meet you.")`` queue the greeting. The text is synthesized by EdgeTTS (voice ``en-US-JennyNeural``, volume 50) on the Internet and played through the carrier's speaker; no API key is needed. Because the greeting runs in its own background thread with a queue, the long speech task never stalls face detection.

**The dead zone** — ``track_face()`` compares the face's center with the exact center of the 640×480 frame. Offsets smaller than 10% of the frame width (64 px) or height (48 px) are ignored. Without this dead zone, even the tiniest face wobble would nudge a servo, and the servo's movement would nudge the face in the frame, creating an endless jitter loop. Inside the dead zone, the servos rest.

**One degree at a time** — When the face drifts beyond the dead zone, Python calls ``Bridge.call("pan_step", ±1)`` or ``Bridge.call("tilt_step", ±1)``. In the sketch, each call adds or subtracts a single degree — ``STEP_DEGREES = 1`` — and writes the new angle to the servo. The sketch constrains the pan between 45° and 135° and the tilt between 45° and 115°, so the camera can never over-rotate and hit its mount. Small, frequent steps are what make the motion look smooth and alive instead of snappy.

**The lost-face timeout** — A background thread checks every 0.2 s whether any detection has refreshed ``last_face_time`` within the last 2.5 seconds. If not, it calls ``center_pan_tilt``, which drives both servos back to 90°, and tells the Web UI the camera is **Looking for a face**. The ``face_visible`` flag resets too — so the next face that walks in is a new "visit" and earns a brand-new greeting.

3. Experiment
----------------

**Follow the Camera**

Try each of these with the app running and observe what the pan-tilt does:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - What you do
     - What the camera does
   * - Step in front of the camera and hold still
     - Greets you once with "Nice to meet you.", then holds the face in the center of the frame
   * - Move slowly left and right
     - The pan servo turns to keep your face centered — about 1° per tracking step
   * - Duck down and stand up
     - The tilt servo moves up and down to follow you
   * - Wobble just a tiny bit (a few centimeters)
     - Nothing — you're inside the 10% dead zone, and the servos stay quiet
   * - Walk away out of view
     - After 2.5 seconds the pan-tilt returns to center and the status reads "Looking for a face"
   * - Step back into view
     - Greets you again — this counts as a new visit

**Challenge: How Fast Can It Follow?**

Walk across the room in front of the camera — first at a slow stroll, then briskly, then a jog. Watch how the pan servo keeps up. Each detection moves the servo only 1°, so what happens when you outrun the frame rate? Is the tracking smoother with slow, steady movement or fast, jerky movement? Can you find a speed where the camera visibly lags behind you?

**Challenge: Two Faces**

Ask a friend to stand beside you, and have both of you face the camera. Which one does the camera follow when you're at different distances? Try slowly swapping who stands closer to the camera — notice how the pan-tilt switches targets. Then have one person leave the frame while the other stays: does the board greet the remaining person again? The greeting fires only when *no face at all* has been seen for 2.5 seconds — observe whether that matches what happens.

4. Troubleshooting
--------------------

**The camera doesn't react to my face at all**

* **Cause:** The camera is not enabled, or the app isn't seeing the model output.
* **Solution:** Check that external carriers are enabled with the camera set to **type1-2lanes** (see the note in Setup). Make sure your face is well-lit and roughly centered, 0.5–2 meters away — the face-detection model needs a clear view of eyes, nose, and mouth.

**The greeting never plays**

* **Cause:** The TTS runtime is still being prepared, or the board has no Internet access.
* **Solution:** The first TTS run can take half an hour to download dependencies — watch the Console for ``EdgeTTS ready.`` before expecting speech. EdgeTTS synthesizes audio online, so keep the UNO Q connected to the Internet. If a TTS error appears on the Console, re-run the app once the setup has completed.

**The servos don't move, or jitter and chatter**

* **Cause:** The battery pack is not connected — USB power alone is too weak for two metal-gear servos under load.
* **Solution:** Connect the battery pack to the Robot Shield. Also check that the pan servo is plugged into **D9** and the tilt servo into **D10**, with the cable's brown wire toward the outside edge of the header.

**The camera feed in the Web UI is black**

* **Cause:** The video stream (served on port 4912) hasn't loaded yet, or the camera isn't enabled.
* **Solution:** Wait a moment — the page retries the stream every second automatically. If it stays black, reboot the board after enabling the camera carrier setting, then click **Run** again.

**The board greets me again and again while I'm standing still**

* **Cause:** Detection is flickering in and out faster than you think.
* **Solution:** This shouldn't happen with a steady, well-lit face — the debounce and the 2.5 s timeout normally suppress it. If it does happen, you're probably right at the edge of the detection range, where confidence dips below 0.5 between frames. Move a little closer or improve the lighting, and the greeting will settle back to once per visit.

5. Summary
-------------

You just built a camera that sees you, speaks to you, and follows you around — a tiny robot companion! In this lesson, you learned:

* How to track a face with two servos, moving the pan and tilt independently
* Why a dead zone keeps servo tracking smooth and jitter-free
* How one-degree incremental steps create fluid, natural motion
* How a timeout state (face lost for 2.5 s) returns the system to "ready" automatically
* How a background TTS thread speaks greetings without ever blocking the AI

In the next lesson, you'll turn this tracking talent into a real security system — one that patrols, detects intruders by their whole body, and raises the alarm.
