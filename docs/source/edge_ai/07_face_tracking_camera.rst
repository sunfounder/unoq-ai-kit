.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

07 Face Tracking Camera
=======================

The gesture camera moved, but only in fixed steps: one gesture, one 15° nudge, then it waited for you to leave the frame. What if the camera could *keep its eyes on you* instead? In this lesson, the UNO Q not only detects your face — it **follows it**. The pan-tilt camera greets you, then tracks you as you move left, right, up, and down, like a tiny robot that wants to keep you in the center of its view.

.. image:: img/07_face_tracking_camera.png
   :width: 600
   :align: center

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

**Wiring Diagram**

This lesson uses no breadboard components — everything plugs into the Robot Shield. Plug the pan servo into pin **D9** and the tilt servo into pin **D10** on the Robot Shield's servo headers.

.. image:: /img/wiring/wiring_pan_tilt.png
   :width: 600
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

#. Download :download:`07 Face Tracking Camera.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/07.Face.Tracking.Camera.zip>` and import it in App Lab.

#. The app appears in **Apps** — click it to open.

#. The pan-tilt servos draw more power than the USB port alone can provide, so connect the battery pack to the Robot Shield.

#. Click the **Run** button (▶). The servos move to the 90° center position. On the Console you'll see the Python side announce itself: ``Face Tracking Camera with TTS is running.``, and once the speech engine is ready, ``EdgeTTS ready.`` The sketch prints its own banner, ``=== Face Tracking Camera ===``, over the serial connection.

#. Open the **Web UI** tab. The live camera feed fills the page, and a status area reports **Looking for a face** — "The pan-tilt is centered and waiting."

#. Stand in front of the camera. The board greets you with *"Nice to meet you."* and the status flips to **Face detected** — "The pan and tilt servos are following the face."

#. Move left and right, then duck and rise. The camera follows you to keep your face centered. Now step out of view and count to three — after about 2.5 seconds the camera returns to center, the status goes back to **Looking for a face**, and the next face that appears triggers a fresh greeting.

.. image:: img/07_face_tracking_camera.png
   :width: 600
   :align: center

.. note::

   The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

**How it Works**

Now that you've seen the camera follow you, here is what happens between a face appearing in the frame and a servo moving.

An App Lab project is a folder containing multiple files. Here's what each one does:

* ``07 Face Tracking Camera/`` — the app folder

  * ``app.yaml`` — App metadata: declares the ``video_object_detection``, ``web_ui``, and ``sunfounder_tts`` bricks

  * ``python/``

    * ``main.py`` — Face detection, greeting speech, and the tracking decisions

  * ``sketch/``

    * ``sketch.yaml`` — Sketch configuration (declares the ``Arduino_HardwareServo`` library)
    * ``sketch.ino`` — Servo control on the microcontroller

  * ``assets/``

    * ``index.html`` — Web UI structure (camera frame and face status)
    * ``app.js`` — Browser logic: camera stream and Socket.IO events
    * ``style.css`` — Visual styling
    * ``libs/`` — JavaScript libraries (Socket.IO)
    * ``img/`` — Static resources

  * ``README.md`` — Project documentation and usage guide

The data path from a face in front of the camera to a servo movement — and back:

.. mermaid::

   sequenceDiagram
       participant C as Camera (CSI)
       participant P as Python (main.py)
       participant S as Sketch (sketch.ino)
       participant B as Browser (HTML/JS)

       C->>P: frame (flipped vertically)
       P->>P: VideoObjectDetection → send_detections()
       P->>P: box_center() vs. the middle of the frame
       P->>P: EdgeTTS speaks "Nice to meet you." — first sighting only
       P-->>B: face_status {detected: true}
       P->>S: Bridge.call("pan_step", ±1)
       P->>S: Bridge.call("tilt_step", ±1)
       S->>S: servo.write(angle) — one degree, clamped
       P->>S: Bridge.call("center_pan_tilt", "") — no face for 2.5 s
       P-->>B: face_status {detected: false}

Here's what each component does:

**Sketch (sketch.ino)** — runs on the STM32 MCU
  * ``panServo.attach(9)`` and ``tiltServo.attach(10)`` bind the servos to **D9** (pan) and **D10** (tilt)
  * ``Bridge.provide()`` registers the three functions Python may call — ``pan_step``, ``tilt_step``, and ``center_pan_tilt``
  * ``panStep()`` and ``tiltStep()`` add or subtract a single degree (``STEP_DEGREES = 1``), clamp the result with ``constrain()`` — pan 45°–135°, tilt 45°–115° — and write it to the servo
  * ``centerPanTilt()`` sends both servos back to 90°
  * ``loop()`` only sleeps — every movement arrives as a Bridge call

**Python (main.py)** — runs on the Linux MPU
  * ``Camera(adjustments=lambda frame: frame[::-1, :])`` flips every frame vertically, because the CSI camera is mounted upside down on the carrier
  * ``VideoObjectDetection(camera, confidence=0.5, debounce_sec=0.1)`` runs the **face-detection** model on each frame
  * ``detection.on_detect_all(send_detections)`` hands every detection to ``send_detections()``, which keeps the most confident face using ``box_center()``
  * ``track_face()`` compares that face center with the middle of the 640 × 480 frame and calls ``Bridge.call("pan_step", ±1)`` or ``Bridge.call("tilt_step", ±1)`` only when the offset leaves the dead zone
  * ``speak()`` puts the greeting on a queue for EdgeTTS, which runs in its own daemon thread
  * ``monitor_face_status()`` checks the clock every 0.2 s and calls ``Bridge.call("center_pan_tilt", "")`` after ``FACE_LOST_TIMEOUT = 2.5`` seconds without a face
  * ``ui.send_message("face_status", …)`` tells the browser whether a face is being followed
  * ``App.run()`` starts the app

**Bridge** — communication channel between MPU and MCU
  * Python side: ``Bridge.call("pan_step", direction)`` invokes a sketch function across the two processors
  * Sketch side: ``Bridge.provide("pan_step", panStep)`` exposes that function
  * Only a direction (``+1`` or ``-1``) crosses the Bridge — the sketch owns every angle

**Browser (HTML/JS)** — runs in the user's browser
  * The camera feed is an ``<iframe>`` pointed at the stream URL on port 4912 (``/embed``), reloaded once a second until it appears
  * ``socket.on("face_status", …)`` switches the label between **Face detected** and **Looking for a face**, and updates the hint text below it
  * ``socket.on("connect")`` and ``socket.on("disconnect")`` drive the status dot and the "Connection lost" banner

**Why the dead zone?** — Offsets smaller than 10% of the frame (64 px horizontally, 48 px vertically) are ignored. Without that margin, even the tiniest wobble in the detected box would nudge a servo; the servo would then move the face in the frame, which nudges the box again, and the two would chase each other in an endless jitter loop. Inside the dead zone, the servos simply rest.

**One greeting per visit** — The greeting is not triggered by every detection, or the board would chatter nonstop. The ``face_visible`` flag remembers whether a face is already being followed, so only the moment it flips from *lost* to *found* queues ``speak("Nice to meet you.")``. The sentence is synthesized by EdgeTTS (voice ``en-US-JennyNeural``, volume 50), which works **online — an Internet connection is required, but no API key**. Because it runs on its own worker thread with a queue, a sentence that takes a second to produce never stalls face detection.

**One degree at a time** — The AI never decides where to point the camera; it only reports where the face is, in numbers. Python turns that into a direction, and the sketch turns the direction into a small, safe movement. One degree per call, several calls per second, is what makes the motion look smooth and alive instead of snappy — and because the sketch clamps every angle to the servo's safe range, a badly framed face can never drive the mechanism past its limits.

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
