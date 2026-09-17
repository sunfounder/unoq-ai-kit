.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

01 AI Vision Recognition
==========================

By now your UNO Q has streamed a live camera feed to a Web UI, and you have been the one watching it and deciding what it means. This lesson flips that around: point the camera at a cup, a person, or a cell phone, and the board itself recognizes what it is looking at — in real time, entirely on the device, with no cloud involved. The detected objects appear on screen, side by side with the live video, each labeled with its name and a confidence score.

.. image:: img/01_ai_vision_recognition.png
   :width: 600
   :align: center

In this lesson, you will learn to:

* Start the CSI camera from Python and flip every frame so the preview is upright
* Run the ``VideoObjectDetection`` brick with its general model, and tune the ``confidence`` and ``debounce_sec`` settings
* Read the detections dictionary the model produces and turn it into readable results
* Push live detection results to a custom Web UI over socket.io, complete with icons and confidence bars

1. Setup
-----------

**What You Need**

.. list-table::
   :widths: 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * USB-C Cable
   * - |list_pan_tilt|
     - |list_usb_cable|

.. note::

   Before using the camera, make sure external carriers are enabled on your UNO Q — this is a one-time setup: :ref:`enable_external_carriers`.

No breadboard wiring is needed in this lesson. The CSI camera is already attached to the Multimedia Carrier, which is part of your pre-assembled kit — the only "circuit" here is the light entering the lens.

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

#. Navigate to the ``unoq-ai-kit/edge_ai/`` folder and select ``01 AI Vision Recognition.zip``.

#. The app appears in **Apps** — click it to open.

**Run the Code**

#. With the app open, click the **Run** button (▶) in the top-right corner. The app boots the camera and loads the AI model, which takes a few seconds the first time.

   .. image:: /img/app_run.png
      :width: 500
      :align: center

#. The Output window prints:

   *"🤖 AI Vision Recognition running — open the Web UI."*

   A **Web UI** tab opens automatically, showing two cards: the live camera feed on the left, and a **Detected Objects** panel on the right.

#. When the video appears, the status dot turns blue and the label changes from **Connecting** to **Connected**, with the hint text reading *"AI detecting objects in real time"*. The Detected Objects panel starts with the placeholder *"Point the camera at an everyday object"*.

#. Show the camera an everyday object — a cup works well. Within a moment, the object appears in the Detected Objects panel with an icon, its name (``cup``), and a confidence percentage: the higher the percentage, the more certain the model is. A blue bar under the name shows the same score at a glance.

#. Try a person and a cell phone too — each detection row shows its own icon, name, and confidence.

**The Code**

**Python (main.py)** — runs on the Linux MPU: camera, object detection, and Web UI

.. code-block:: python
   :linenos:

   # SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
   #
   # SPDX-License-Identifier: MPL-2.0

   """
   AI Vision Recognition — detect common objects in the camera feed.

   The VideoObjectDetection brick (with no model restriction) detects
   common objects in the camera feed. Detections are sent to the custom
   Web UI via socket.io and displayed alongside the live video stream.
   """

   from datetime import datetime, UTC
   from arduino.app_utils import App
   from arduino.app_bricks.web_ui import WebUI
   from arduino.app_bricks.video_objectdetection import VideoObjectDetection
   from arduino.app_peripherals.camera import Camera

   # Serve our custom web interface
   ui = WebUI()

   # Start the CSI camera
   camera = Camera(adjustments=lambda frame: frame[::-1, :])
   camera.start()

   # Video object detection — general model for common objects
   detection = VideoObjectDetection(camera, confidence=0.4, debounce_sec=1.0)

   # Send all detections to the web UI
   def send_detections(detections: dict):
       """Called for every frame with detection results."""
       results = []
       for class_name, instances in detections.items():
           for instance in instances:
               results.append({
                   "object": class_name,
                   "confidence": round(instance.get("confidence", 0) * 100),
                   "timestamp": datetime.now(UTC).isoformat(),
               })

       if results:
           ui.send_message("detections", {"objects": results})


   detection.on_detect_all(send_detections)

   print("🤖 AI Vision Recognition running — open the Web UI.")

   App.run()

Everything else in the project supports this file: the ``assets/`` folder holds the Web UI pages (``index.html``, ``app.js``, ``style.css``, and the socket.io client library), and ``app.yaml`` declares the two bricks the app relies on — ``web_ui`` and ``video_object_detection``.

**How it Works**

.. code-block:: text

   camera frames → vertical flip (frame[::-1, :]) → VideoObjectDetection
   general object model (confidence ≥ 0.4, debounce 1.0 s)
       → on_detect_all → send_detections() → confidence as a percentage
       → ui.send_message("detections", ...) over socket.io
   Browser: video stream (port 4912 /embed) in the left card,
            detection rows with icons and bars on the right

In this lesson the entire project runs on the Linux MPU as a single Python program — the sketch half of the app is an idle placeholder, because object detection happens entirely on the Linux side. The work is split across three pieces that cooperate: the ``Camera`` peripheral produces frames, the ``VideoObjectDetection`` brick interprets them, and the ``WebUI`` brick delivers the result to your browser.

**Capturing frames** — ``Camera`` is an App Lab peripheral, not a brick. Once ``camera.start()`` is called it keeps producing frames in the background. Its ``adjustments`` parameter is a function applied to every frame before anything else sees it; ``lambda frame: frame[::-1, :]`` reverses the rows, flipping the picture top-to-bottom. The CSI camera is mounted upside down in this kit, so without this flip the whole preview would be upside down.

**Turning pixels into objects** — ``VideoObjectDetection(camera, confidence=0.4, debounce_sec=1.0)`` wraps the camera with a pre-trained AI model. Because no specific model is requested, the brick uses its general model, which recognizes roughly 80 common object categories — cups, people, cell phones, bottles, books, and many more. The two settings control how picky it is: ``confidence=0.4`` means any detection the model is less than 40% sure about is discarded, and ``debounce_sec=1.0`` means the same object can trigger a callback at most once per second, so it cannot spam Python with rapid repeated events.

**From detections to data** — ``detection.on_detect_all(send_detections)`` registers a callback that fires with a dictionary: each key is a class name like ``"cup"``, and its value is a list of every instance of that class found in the frame. ``send_detections()`` flattens that dictionary into a plain list of records, converting each instance's confidence (a fraction between 0 and 1) into a whole percentage with ``round(instance.get("confidence", 0) * 100)``, and stamps each one with the current time.

**Getting the results to the screen** — The browser never runs a model; it only renders data. Python sends each batch of results with ``ui.send_message("detections", {"objects": results})``, a socket.io event that ``app.js`` listens for. The page rebuilds its list of detection rows from the payload — each row's icon, name, and confidence bar are pure HTML. The live video, meanwhile, travels on a separate channel: the page embeds the camera stream (served on port 4912 as an ``/embed`` page) in an ``<iframe>``, so pixels and detections stay nicely decoupled. Note that Python only sends a message when at least one object is detected — while the view stays empty, the panel simply keeps whatever it showed last.

3. Experiment
----------------

**Watch the Confidence Score Move**

The percentage under each object name is a window into the model's certainty. Wiggle the inputs and watch it respond:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - You do
     - Result
   * - Hold a cup about 30 cm from the camera in good light
     - A ``cup`` row appears with a high confidence percentage
   * - Move the cup closer
     - The confidence climbs and the blue bar lengthens
   * - Move the cup far away, into a dim corner
     - The percentage drops — below 40% confidence the model stops reporting it altogether
   * - Show several objects at once (a cup and a phone)
     - Every recognized object gets its own row with its own score
   * - Move everything out of view
     - No new detections arrive; the last rows stay on screen until the next detection message replaces them

**Challenge: Explore the Model's Limits**

The general model knows around 80 common categories — but it cannot recognize everything. Walk around your desk and test objects whose icons are built into the page (a book, bottle, chair, laptop, mouse, keyboard, or clock), then try something unusual, like a small toy or a kitchen utensil. Which objects does the model name confidently, and which never appear at all? Also try the same object under different lighting and distances, and see how far you can move it away before its confidence drops below the 40% line. There is no right answer to find — the goal is to feel where the model's abilities end, because later projects rely on knowing exactly what your model can and cannot see.

4. Troubleshooting
--------------------

**The camera area stays black**

* **Cause:** External carriers were never enabled, or the camera port was not enabled before rebooting.
* **Solution:** Complete the one-time setup — enable external carriers and select the camera type for the connector your camera uses, then reboot: :ref:`enable_external_carriers`. After the reboot, stop and run the app again.

**The page shows Connected but no detections ever appear**

* **Cause:** The object is too small, too far away, or too dark for the model, or it is simply not among the ~80 common categories the general model knows.
* **Solution:** Bring the object close (30 cm or less), keep it in good light, hold it still for a moment, and start with one of the guaranteed examples — a cup, a person, or a cell phone. Remember that detections below 40% confidence are discarded.

**The status shows Disconnected and the app's error banner appears**

* **Cause:** The browser lost its socket connection to the app — the app was stopped, or the board connection dropped.
* **Solution:** Stop the app and run it again, then refresh the Web UI tab. If the board is unplugged, reconnect the USB-C cable first.

**Detections feel slow to appear at first**

* **Cause:** The model needs a few seconds to load after the app starts, and the 1-second debounce deliberately paces repeat detections of the same object.
* **Solution:** Wait a few seconds after Run before judging. If a detection still does not appear, move the object closer and keep it steady.

5. Summary
-------------

You just gave your UNO Q a pair of AI eyes — the board can now look at a scene and tell you what is in it, all by itself. Along the way you met the pattern that every project in this module will reuse:

* The ``Camera`` peripheral feeds frames to an AI brick
* ``VideoObjectDetection`` with ``confidence`` and ``debounce_sec`` controls how the model reports what it sees
* ``on_detect_all`` delivers detections to Python as plain data
* A socket.io ``send_message`` puts that data on screen next to the live stream

But so far the AI only *reports* what it sees — it does nothing about it. In the next project, the AI's decision will reach out of the screen and into the real world: the moment the camera sees a face, a buzzer will sound.
