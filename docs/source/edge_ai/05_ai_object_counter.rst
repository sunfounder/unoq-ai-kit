.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

05 AI Object Counter
======================

The gesture project read *you* — one hand signal, one LED. This project goes back to watching the world, but asks a different kind of question: not *what is it?* but *how many?* Many real systems need a running tally: how many boxes passed on a conveyor belt, how many people walked through a door. In this lesson, you'll build an AI counter. The UNO Q watches the camera and counts how many times three everyday objects appear — a computer **mouse**, a **keyboard**, and a **cell phone** — showing the totals live in a Web UI and announcing every new count out loud.

.. image:: img/05_ai_object_counter.png
   :width: 600
   :align: center

In this lesson, you will learn to:

* Filter detection results down to exactly three target classes
* Count detection **events**, not video frames — the core trick behind any AI counter
* Use re-arm state so the same object is never counted twice in one appearance
* See live counts in the Web UI and reset them with a button
* Announce each new count with online text-to-speech

1. Setup
----------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * USB-C Cable
     - -
     - -
   * - |list_pan_tilt|
     - |list_usb_cable|
     - -
     - -

All the hardware is already on the kit: the camera sees the objects, and the Multimedia Carrier's built-in speaker does the talking — no breadboard wiring needed.

To test the project, gather three objects you probably already have nearby: a computer **mouse**, a **keyboard**, and a **cell phone**. The spoken announcements use an online text-to-speech voice, so the UNO Q also needs an **internet connection**.

.. note::

   Before using the camera, make sure external carriers are enabled on your UNO Q — this is a one-time setup: :ref:`enable_external_carriers`.

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

#. Download :download:`05 AI Object Counter.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/05.AI.Object.Counter.zip>` and import it in App Lab.

#. The app appears in **Apps** — click it to open.

#. Click the **Run** button (▶). The output console prints:

   ``AI Object Counter is running. Show one mouse, keyboard, or cell phone at a time.``

   The sketch in this project is just an empty stub — every part that matters runs on the Linux MPU.

#. While the TTS engine prepares itself, the console prints ``TTS ready.``

   .. note::

      The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

#. Open the **Web UI** tab. You'll see the live camera feed, three counter cards — MOUSE, KEYBOARD, and PHONE, all at 0 — and a **TOTAL OBJECTS** counter. The panel above the cards reads "Show one object to the camera".

#. Hold a computer mouse in front of the camera. When the model reaches **60% confidence**, the mouse counter changes from 0 to 1 with a +1 flash, the panel reads **Mouse added** with the confidence percentage, the speaker says *"Mouse detected"*, and the console prints a line like:

   ``Counted mouse: 1 (87%)``

#. Keep the mouse in view — the counter stays at 1 no matter how long it stays. Move the mouse away completely and show it again: the counter goes to 2, then 3, and so on for every new appearance. Repeat with a keyboard and a cell phone — each has its own counter, and the speaker announces *"Keyboard detected"* and *"Cell phone detected"*.

#. Click **RESET COUNTS** — all three counters and the total return to 0.

**How it Works**

Here is what happens between showing an object and hearing its name — a chain that runs almost entirely inside Python on the Linux MPU:

* ``05 AI Object Counter/`` — the app folder

  * Bricks

    * ``video_object_detection`` — the object-detection model, declared as ``arduino:video_object_detection`` in ``app.yaml``
    * ``web_ui`` — the Web UI server and socket channel
    * ``sunfounder_tts`` — online text-to-speech through the carrier's speaker

  * Sketch libraries

    * None — the sketch is an empty stub and declares no libraries

  * Files

    * ``assets/``

      * ``index.html`` — Web UI structure: camera feed, counter cards, reset button
      * ``app.js`` — Browser logic (Socket.IO client and reset request)
      * ``style.css`` — Visual styling
      * ``libs/`` — JavaScript libraries (Socket.IO)
      * ``img/`` — Static resources

    * ``python/``

      * ``main.py`` — Detection, counting state machine, Web UI, and speech

    * ``sketch/``

      * ``sketch.yaml`` — Sketch configuration
      * ``sketch.ino`` — Empty stub; this project needs no MCU-side hardware

    * ``README.md`` — Project documentation and usage guide
    * ``app.yaml`` — App metadata (name, icon, bricks used)

The data path from frame to count:

.. mermaid::

   sequenceDiagram
       participant C as CSI camera
       participant P as Python (main.py)
       participant S as EdgeTTS (sunfounder_tts)
       participant B as Browser (Web UI)

       C->>P: frame → VideoObjectDetection (confidence ≥ 0.60)
       P->>P: on_detection() → best confidence per target class
       P->>P: class armed and present → counts[label] += 1
       P->>P: disarm class; count missing frames
       P->>P: 10 missing frames → re-arm class
       P->>S: speech_queue.put("Mouse detected")
       S-->>P: tts.say() plays the phrase
       P->>B: ui.send_message("counter_state", ...)
       B->>P: POST /reset-counts
       P->>B: counter_state with counts back at 0

Here's what each component does:

**Python (main.py)** — runs on the Linux MPU
  * Starts the camera with ``Camera(adjustments=lambda frame: frame[::-1, :])`` and ``camera.start()``
  * ``VideoObjectDetection(camera, confidence=0.60, debounce_sec=0.2)`` reports every object it recognizes in each frame
  * ``detection.on_detect_all(on_detection)`` receives those results; ``on_detection()`` keeps only the three entries of ``TARGETS``
  * ``counts[label] += 1`` the first time a class is present while ``armed``, then disarms it so a single appearance is never counted twice
  * ``MISSING_FRAMES_TO_REARM`` (10) consecutive missing frames re-arm the class — the object has to leave the view before it can be counted again
  * ``ui.send_message("counter_state", public_state())`` publishes the counts, the total, and the latest detection as a socket event
  * ``speak()`` puts the object's name into ``speech_queue``; ``speech_worker()`` runs ``EdgeTTS.say()`` on a background thread so detection never pauses
  * ``ui.expose_api()`` publishes ``GET /state`` and ``POST /reset-counts``; reset zeroes the counters but deliberately leaves the armed flags alone

**Browser (index.html / app.js)** — runs in the user's browser
  * Shows the live camera feed, the three counter cards, and the **TOTAL OBJECTS** counter
  * ``socket.on('counter_state')`` flashes the +1 animation and writes the "Mouse added" panel with its confidence
  * ``fetch('/state')`` loads the current counts when the page connects
  * The **RESET COUNTS** button posts to ``/reset-counts`` and redraws the cards at 0

3. Experiment
----------------

**Count Each Target Object**

Show the objects to the camera one at a time and check the results:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - What you do
     - Expected result
   * - Hold up a computer mouse until it counts
     - Mouse counter +1; panel shows "Mouse added"; speaker says "Mouse detected"
   * - Hold up a keyboard
     - Keyboard counter +1; panel shows "Keyboard added"; speaker says "Keyboard detected"
   * - Hold up a cell phone
     - Phone counter +1; panel shows "Cell Phone added"; speaker says "Cell phone detected"
   * - Keep the same object in view for a long time
     - Its counter stays exactly where it was — no repeat counting
   * - Remove the object completely, then show it again
     - Its counter goes up by one more for every new appearance
   * - Click **RESET COUNTS**
     - All counters and the total return to 0

**Challenge: Where Does the Counter Stop?**

Walk backwards while holding a mouse until the model's confidence drops below 60% — that's the moment counting stops. Try each object: which one stays recognizable from the farthest distance? Then repeat in dim light and note how much closer you have to stand. The 60% line is not a wall; confidence drifts with distance, lighting, and angle, and the counter only trusts detections above the line.

**Challenge: Two Targets at Once**

Show a mouse and a keyboard together in the same frame. Each class has its own armed state, so both counters rise together — one count each. Now hold up two mice at the same time: only one count appears, because the *class* is counted, not individual instances. What happens if you remove one mouse while the other stays? Watch the counter card and try to predict the rearm behavior.

4. Troubleshooting
--------------------

**The counters never increase, even with an object in view**

* **Cause:** The model's confidence stays below the 60% threshold — the object is too far, too small, poorly lit, or not one of the three target classes.
* **Solution:** Hold the object 0.5–1.5 m from the camera, roughly centered, in good light. Only mice, keyboards, and cell phones are counted — a notebook or coffee cup will never move a counter, by design.

**An object counts twice while it never left the view**

* **Cause:** The object briefly left the frame — or was only half-visible at the edge — for the 10-frame rearm window, so the class armed itself again.
* **Solution:** Keep the object fully and continuously in view for one appearance. For a clean sequence, remove it completely between appearances, as the Web UI hint says: "Remove the object from view before counting another one."

**Counting works in the Web UI, but there is no voice**

* **Cause:** The TTS runtime is still being prepared on the first run, the internet connection is down, or the TTS engine failed to start.
* **Solution:** Wait for the one-time TTS setup described in the note above and keep the UNO Q online — EdgeTTS synthesizes speech in the cloud, so it needs internet on every run. Watch the console: it should print ``TTS ready.``; if it prints ``TTS startup failed: ...`` instead, check the network and run the app again. Counting and the Web UI keep working either way.

**RESET COUNTS returns to zero, but the object on screen isn't counted again**

* **Cause:** Reset zeroes the counters but deliberately leaves the armed states untouched.
* **Solution:** Remove the object from view and show it again — once it has been absent long enough to rearm, the next appearance counts as a fresh event.

**The Web UI shows a black screen or "Disconnected"**

* **Cause:** The camera is not enabled, the app stopped running, or the board disconnected.
* **Solution:** Enable external carriers (see :ref:`enable_external_carriers`) and check the camera's FFC ribbon cable — the blue side faces up and both ends must click securely. Then click **Run** in App Lab and check the USB-C cable is firmly connected at both ends.

5. Summary
-------------

You built your first AI *event counter* — not just a classifier, but a small state machine that turns a stream of frames into meaningful events. In this lesson, you learned:

* How to filter detections to the three classes your project targets
* Why counting events instead of frames matters, and how the armed/rearm pattern makes it work
* How to expose live state and actions to a Web UI through socket.io events and web APIs
* How a speech worker thread adds voice feedback without ever blocking detection

In the next project, gestures come back — and this time they do more than switch a light. One gesture tilts the camera, another returns it to the centre, another takes a photo, and the UNO Q tells you out loud what it just did.
