.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

04 AI Gesture Light
===================

The previous project taught the camera to tell *what* it was looking at, and the RGB LED showed that answer as a colour. This project asks a slightly different question: not "what object is this?" but "which one of a few known categories is this?" — and then lets the answer flip a piece of hardware on and off. Show the camera a 👍 thumbs up and an LED lights up; show it a ✊ fist and the LED goes dark. Two more gestures, the ✌️ V-sign and the 🖐️ open hand, are recognized and named on screen but deliberately leave the LED alone.

.. image:: img/04_ai_gesture_light.png
   :width: 600
   :align: center

In this lesson, you will learn to:

* Run a **classification** model — ``hand-gestures`` — whose output is one of four fixed labels, and read the label's confidence
* Map a label directly to a hardware state and send it to the sketch over the Bridge
* Act only when the recognized label *changes*, instead of firing on every camera frame
* Reset the display automatically after the hand leaves the camera's view

1. Setup
----------

**What You Need**

.. list-table::
   :widths: 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_led` (Red)
   * - 1 * :ref:`cpn_resistor` (220Ω)
     - 1 * USB Cable
   * - |list_pan_tilt|
     - |list_red_led|
   * - |list_220ohm|
     - |list_usb_cable|

**Software Requirements**

This project uses the following Bricks (declared in ``app.yaml``):

* ``arduino:video_object_detection`` with ``model: hand-gestures`` — runs the **hand-gesture classification** model on every camera frame
* ``arduino:web_ui`` — serves the Web UI with the live camera feed, the current gesture card, and the gesture hint line

The sketch uses no external libraries — only the built-in Bridge library from the Arduino framework.

.. note::

   Before using the camera, make sure external carriers are enabled on your UNO Q — this is a one-time setup: :ref:`enable_external_carriers`.

**Wiring Diagram**

This is a one-component circuit on a breadboard: the LED's **anode** (the longer leg) goes to **D5** through a **220Ω resistor**, and its **cathode** (the shorter leg, the flat side of the body) goes to **GND**. The resistor is not optional — without it the LED draws far more current than it can survive.

.. image:: /img/wiring/wiring_led.png
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

#. Navigate to the ``unoq-ai-kit/edge_ai/`` folder and select ``04 AI Gesture Light.zip``.

#. The app appears in **Apps** — click it to open.

#. Click the **Run** button (▶). The app boots the camera and loads the hand-gesture model, which takes a few seconds the first time. The Output window prints:

   *"AI Gesture Light is running — show your hand to the camera."*

   A **Web UI** tab opens automatically, showing the live camera feed with a **Current Gesture** card underneath it.

   .. image:: /img/app_run.png
      :width: 500
      :align: center

#. While the page is still starting, the status dot is grey and the label reads **Connecting...**, with the placeholder text *"Show your hand to the camera"*. Once the camera stream and the socket connection are both up, the dot turns teal and the label reads **Connected**.

#. Hold your hand about 50 cm in front of the camera against a plain background and give it a 👍 **thumbs up**. The Current Gesture card fills in — the gesture name **Thumbs up**, a confidence percentage such as ``87%``, and the action **LED ON** — and the LED on your breadboard lights up.

#. Change to a ✊ **fist**. The card now shows **Fist**, its own confidence, and **LED OFF** — and the LED goes dark.

#. Try a ✌️ **V-sign**, then a 🖐️ **open hand**. Both are recognized and named in the card, but the LED does not change — those two gestures are display-only in this project.

#. Take your hand out of the frame and wait about two seconds. The card clears back to **Waiting...** with *"Confidence: --"* and the action line **Show a gesture**.

**How it Works**

A single gesture now crosses four layers — the model labels it, Python decides whether the label means anything, the sketch moves the pin, and the page reports what happened.

An App Lab project is a folder containing multiple files. Here's what each one does:

* ``04 AI Gesture Light/`` — the app folder

  * Bricks

    * ``video_object_detection`` with ``model: hand-gestures`` — runs the hand-gesture classification model on every camera frame
    * ``web_ui`` — serves the Web UI with the live camera feed, the Current Gesture card, and the gesture hint line

  * Sketch libraries

    * None — the sketch only uses the built-in Bridge library

  * Files

    * ``assets/``

      * ``index.html`` — Web UI structure (camera feed, Current Gesture card, hint line)
      * ``app.js`` — Browser logic (Socket.IO client and card updates)
      * ``style.css`` — Visual styling
      * ``libs/`` — JavaScript libraries (Socket.IO)
      * ``img/`` — UI images (logo)
      * ``docs_assets/`` — Documentation images (result and wiring diagrams)

    * ``python/``

      * ``main.py`` — Camera, gesture classification, edge-triggered actions, and the reset thread

    * ``sketch/``

      * ``sketch.yaml`` — Sketch configuration
      * ``sketch.ino`` — LED control on the microcontroller

    * ``README.md`` — Project documentation and usage guide
    * ``app.yaml`` — App metadata (name, icon, bricks used)

The data path, from a raised hand to a lit LED:

.. mermaid::

   sequenceDiagram
       participant C as Camera (CSI)
       participant P as Python (main.py)
       participant S as Sketch (sketch.ino)
       participant B as Browser (HTML/JS)

       C->>P: video frames
       P->>P: hand-gestures model → best_gesture()
       P->>P: same label as last time? then nothing happens
       P->>S: Bridge.call("set_led", 1)
       S->>S: digitalWrite(5, HIGH)
       P-->>B: gesture_result {gesture, confidence, action}
       B->>B: update the Current Gesture card
       P-->>B: 2 s without a gesture → "Show a gesture"

Here's what each component does:

**Sketch (sketch.ino)** — runs on the STM32 MCU
  * ``digitalWrite(LED_PIN, state ? HIGH : LOW)`` switches **D5**
  * ``setLed()`` takes a plain integer — Python sends ``1`` or ``0``, never a gesture name
  * ``Bridge.provide("set_led", setLed)`` registers the function Python is allowed to call
  * ``setup()`` drives the pin LOW once so the LED starts dark, and ``loop()`` only delays — all the real work is event-driven

**Python (main.py)** — runs on the Linux MPU
  * ``VideoObjectDetection(camera, confidence=0.25, debounce_sec=0.2)`` runs the hand-gesture model locally
  * ``best_gesture()`` ignores any label that is not in ``GESTURE_NAMES`` and returns the highest-confidence one
  * ``on_detections()`` compares the new label with ``last_gesture`` and returns early when the two match
  * ``set_led()`` calls ``Bridge.call("set_led", 1 if state else 0)``, and only for ``good`` (thumbs up) and ``neut`` (fist)
  * ``send_result()`` pushes the gesture name, the confidence as a percentage, and an action string to the browser
  * ``reset_when_gesture_is_lost()`` runs in a background thread and clears the stored label after ``GESTURE_LOST_TIMEOUT`` (2 seconds)

**Bridge** — the communication channel between the MPU and the MCU
  * Sketch side: ``Bridge.provide("set_led", setLed)`` exposes the LED function
  * Python side: ``Bridge.call("set_led", 1)`` invokes it with one integer
  * Keeping the gesture vocabulary on the Linux side leaves the MCU with nothing to interpret — it just switches a pin

**Browser (HTML/JS)** — runs in the user's browser
  * ``socket.on('gesture_result', ...)`` writes the gesture name, the confidence, and the action into the Current Gesture card
  * ``setDefaultUI()`` runs on page load, before the socket connects, so the card starts at **Waiting...** / **Confidence: --**
  * The live video travels on its own channel: ``app.js`` embeds the camera stream from port 4912 in an ``<iframe>``
  * ``socket.on('connect')`` and ``socket.on('disconnect')`` drive the status dot, independently of the gesture card

**A classification model, not an object model** — The general model you used earlier knows around 80 everyday categories and answers *"what is in this picture?"* — it has to consider the whole world. This project requests ``arduino:video_object_detection`` with ``model: hand-gestures``, which replaces that general model with a small, specialized one that answers a narrower question: *"which of my four gestures is this?"* That difference matters in three practical ways. It only ever returns one of its own classes, so you never have to filter out cups and chairs; it is trained specifically on hands, so it still recognizes a gesture when the background is busy; and because its whole world is four possibilities, "something" is always the answer — which is exactly why the confidence threshold has to be low.

**Four labels, four meanings** — The model speaks in short internal labels, and the ``GESTURE_NAMES`` dictionary is the translation table between the model's vocabulary and yours: ``good`` is a 👍 thumbs up, ``neut`` is a ✊ fist, ``five`` is a 🖐️ open hand, and ``peace`` is a ✌️ V-sign. Keeping the mapping in one dictionary means the rest of the program never deals in raw model labels — ``send_result()`` looks a label up with ``GESTURE_NAMES.get(label, "None")`` so the Web UI always shows a human-readable name — and it also decides which labels are *supported*: ``best_gesture()`` skips any class that is not in the dictionary, so if the model ever reports something outside this set, Python ignores it. Only two of the four labels have a hardware consequence: ``good`` calls ``set_led(True)`` and ``neut`` calls ``set_led(False)``, while every other label falls into the ``else`` branch and gets the action string ``"Gesture displayed"`` — recognized, shown, and deliberately harmless.

**Why the threshold is only 0.25** — The object-detection project used a picky threshold of 0.45, because a wrong detection there means the wrong colour or a false alarm. Here ``CONFIDENCE_THRESHOLD = 0.25`` is deliberately permissive, for a reason that comes straight from classification: the model always has to choose one of four classes, so even a half-visible hand gets *some* answer, and that answer's score is spread across four candidates rather than across 80. A stricter threshold would leave you waving at the camera waiting for nothing. The safety net is elsewhere: ``best_gesture()`` also picks the **highest-confidence** instance across all labels, so if the model is uncertain between a thumbs up and a fist, only the stronger guess is acted on.

**Why debounce is a mere 0.2 seconds** — ``debounce_sec=0.2`` is the brick's own rate limit: the model cannot report more often than five times a second. Compare that with the 0.3-second debounce the general model used — that setting exists to stop a *detector* from re-announcing the same object dozens of times per second. Here the pace is different because the model is classifying continuously and you want the display to feel live, while 0.2 s is still long enough to swallow frame-to-frame flicker that would otherwise make the card strobe between labels.

**Act on the change, not on the frame** — This is the heart of the lesson. Detection callbacks fire for *every* frame, so with a hand held in view ``on_detections()`` might run thirty times a second — and thirty times a second it would call ``Bridge.call("set_led", 1)``, hammering the Bridge with messages that all ask for the state the LED is already in. The guard is a timestamp and a comparison. ``last_gesture`` remembers the label that was last *acted on*; if the freshly recognized label is the same one, the function returns immediately — no Bridge call, no socket message, no work at all. Only a genuine **change** of label falls through to the action code. This is called **edge-triggered** behaviour, and it is the habit worth taking away from this project: a model's output is a stream, but your hardware usually cares about transitions in that stream, not about its instantaneous value. Notice that the timestamp is refreshed *before* the comparison, so time keeps counting even while the same gesture is held — which is what the next paragraph needs.

**The two-second reset** — ``reset_when_gesture_is_lost()`` runs in a background thread and wakes every 0.2 seconds to compare ``time.monotonic()`` against ``last_gesture_time``, the stamp that ``on_detections()`` keeps refreshing. If more than ``GESTURE_LOST_TIMEOUT`` (2 seconds) have passed since the last recognized gesture, the thread clears ``last_gesture`` back to ``None`` and sends an empty result, which the browser renders as **Waiting...** / **Show a gesture**. Cleaning up matters for a subtle reason: ``last_gesture`` is not just a label, it is the memory that makes edge-triggering work. Clearing it means that when you bring your hand back, the gesture counts as a fresh change and fires again — hold up a thumbs up, drop your hand, wait two seconds, and the same thumbs up will turn the LED on again. Without that reset, the second thumbs up would look identical to the last one and be silently ignored.

One last detail from the page: the status dot is driven by the socket's ``connect`` and ``disconnect`` events, while the gesture card is driven by ``gesture_result`` messages and the picture arrives on yet another channel. That is why the dot can honestly say **Connected** even before you have shown the camera anything.

3. Experiment
---------------

**Test Each Gesture**

Hold each gesture up to the camera for a second or two, about 50 cm away against a plain background, and watch both the card and the LED:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - You do
     - Result
   * - 👍 Thumbs up (``good``)
     - Card shows **Thumbs up** with a confidence percentage and **LED ON** — the LED lights up
   * - ✊ Fist (``neut``)
     - Card shows **Fist** and **LED OFF** — the LED goes dark
   * - ✌️ V-sign (``peace``)
     - Card shows **V-sign** and **Gesture displayed** — the LED keeps whatever state it had
   * - 🖐️ Open hand (``five``)
     - Card shows **Open hand** and **Gesture displayed** — again, no hardware change
   * - Move your hand out of the frame
     - After about 2 seconds the card returns to **Waiting...** / **Show a gesture**
   * - Show the same thumbs up again, twice in a row
     - Each one is reported once; the LED turns on the first time and simply stays on

**Watch the Confidence Number Move**

The percentage in the card is the model's own certainty, and it reacts to how you present your hand. Hold a thumbs up steady and watch it climb. Move your hand much closer, so it fills the frame, and watch the number change — the model was trained on hands at a typical distance. Turn the hand slightly, or rotate your wrist, and the score usually dips because the silhouette the model sees is no longer the one it learned. Then try the same gestures in a dim room and in bright daylight: lighting is the single biggest influence on this number, and it is worth seeing how far it falls before the label disappears from the card entirely.

**Challenge: Find the Breaking Point of the Threshold**

The card only fills in when the model's score for a class reaches ``CONFIDENCE_THRESHOLD = 0.25``. Open ``python/main.py`` and raise it — try ``0.5``, then ``0.7`` — and re-run the app after each change. How much more carefully do you have to hold each gesture before it registers? At what point does a gesture become impossible to trigger at all? Now set it back down to ``0.1`` and see what the other extreme feels like: does the card start naming gestures when your hand is barely in the frame, or when it is not there at all? Your goal is not one correct number — it is to feel where *your* lighting and background put the comfortable middle.

**Challenge: How Long Does the Memory Last?**

The app forgets your last gesture after ``GESTURE_LOST_TIMEOUT = 2.0`` seconds, and that forgetfulness is what lets the *same* gesture fire twice. Set it to ``6.0`` and experiment: hold up a thumbs up, drop your hand for three seconds, then bring the thumbs up back. What happens? Then set it to ``0.2`` and repeat — is the app more responsive, or does the card start flickering while your hand is still in view? Think about why an app that forgets too eagerly and an app that never forgets are both frustrating to use, and pick the value you would want if you were demonstrating this at a science fair.

4. Troubleshooting
--------------------

**Your gestures are never recognized — the card stays at "Waiting..."**

* **Cause:** Your hand is the wrong size in the frame, the background is cluttered, or the lighting is too dim for the model to read the hand's shape.
* **Solution:** Hold your hand about 50 cm from the camera and keep the **whole hand** inside the frame — if your palm looks huge on screen, move farther back. Use a clean, plain background (a white wall works well) and avoid other objects or a second hand near the camera. Good, even light makes a large difference to this model.

**The card names the gesture, but the LED never changes**

* **Cause:** The LED circuit is wired to the wrong pin, the LED is in backwards, or the Bridge connection to the sketch was never established.
* **Solution:** Check that the **anode** — the longer leg — goes through the 220Ω resistor to **D5**, with the shorter leg to **GND**; an LED only conducts one way, so a reversed one stays dark. Also confirm the sketch's ``Bridge.provide("set_led", setLed)`` ran without error in the Console, because the card can update over socket.io even when the Bridge half has failed.

**The LED changes at the wrong moments — false triggers**

* **Cause:** ``CONFIDENCE_THRESHOLD`` is deliberately permissive at **0.25**, so a partial or ambiguous hand shape can be named as one of the four classes.
* **Solution:** Raise the threshold in ``python/main.py`` — try ``0.5`` — and re-run, until the wrong gestures stop appearing. On the camera side, keep your hand away from patterned backgrounds and out of frame when you are not gesturing, and note that the display-only gestures (✌️ and 🖐️) are the safest way to check what the model is seeing without changing the LED.

**The status shows "Disconnected", or the camera area stays black**

* **Cause:** Two different connections feed this page — the socket to Python (the status dot) and the camera stream (the picture). Losing either one has its own symptom, and the app being stopped breaks both.
* **Solution:** First make sure the app is still running and that external carriers are enabled for the camera (:ref:`enable_external_carriers`). Then stop the app, run it again, and refresh the Web UI tab — the page re-requests the stream every second, so a reload usually brings it back. If the board is unplugged or the Wi-Fi dropped, reconnect it and run the app once more.

5. Summary
-------------

You just taught your UNO Q to read a gesture and answer with hardware — a camera, four classes, and an LED that obeys two of them. In this lesson, you learned:

* How a **classification** model differs from a general object model: it answers with one of its own fixed classes instead of scanning the world
* How to map a model label onto a hardware state and send it to the sketch over the Bridge
* Why a low confidence threshold suits a four-class model, and why the debounce can be as short as 0.2 s
* How **edge-triggered** logic acts only on a change of label, so the same gesture does not repeat its command on every frame
* How a timed reset after two quiet seconds lets the same gesture fire again

So far your projects have each responded to a single thing the camera showed. In the next project, the UNO Q will keep *count* — objects will come and go, and the board will tally them up and announce the total out loud.
