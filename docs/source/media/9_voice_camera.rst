.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

09 Voice-Controlled Camera
============================

This is where everything comes together. No button this time — the microphone listens on its own, in repeating cycles. Say "Take photo" and the camera snaps a picture; say "Turn left" and the pan-tilt moves; every action is confirmed aloud. Speech → command → action → feedback, hands-free.

In this lesson, you will learn to:

* Run a continuous listen-recognize-act loop without any button
* Map voice phrases directly to action functions with a ``COMMANDS`` table
* Combine camera, servos, STT, and TTS in one app
* Recover from errors so one bad cycle doesn't stop the program

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

This project uses the following App Lab Bricks and libraries:

* Bricks:

  * ``sunfounder_stt`` (local speech-to-text, Whisper model)
  * ``sunfounder_tts`` (local text-to-speech, EdgeTTS engine)

* Libraries:

  * ``Arduino_HardwareServo`` (drives the two servo motors)

.. note::

   The project ZIP is large (about 100 MB) because it bundles the local speech recognition model. The first import takes a while — this is normal.

Before using the camera, make sure external carriers are enabled on your UNO Q — this is a one-time setup: :ref:`enable_external_carriers`.

**Wiring Diagram**

Connect the servos to the Robot Shield:

- Pan servo → **D9**
- Tilt servo → **D10**

.. image:: /img/wiring/wiring_pan_tilt.png
   :width: 500
   :align: center

2. Run the App
----------------

#. Open **Arduino App Lab**, import ``09 Voice-Controlled Camera.zip`` from the ``unoq-ai-kit/media/`` folder.

#. Click **Run** (▶). The Output window shows:

   *"Voice-controlled camera is ready. The microphone listens for 4 seconds each time."*

#. Speak a command into the microphone — say "Take photo" and a photo is saved as ``photos/photo_001.jpg``, or say "Turn left" and the pan-tilt moves. The speaker confirms each action, then the microphone listens again automatically.

.. note::

   The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

**How it Works**

.. mermaid::

   sequenceDiagram
       participant S as Sketch (sketch.ino)
       participant P as Python (main.py)

       loop every cycle
           P->>P: stt.start_listening() — 4 seconds
           P->>P: stt.get_result() → "Take photo"
           P->>P: match_command() looks up COMMANDS
           P->>P: action() — take_photo() or servo move
           P->>S: Bridge.call("pan_left", "")
           S->>S: servo moves
           P->>P: tts.say(feedback)
           P->>P: wait 0.8 s, then listen again
       end

**Python (main.py)** — runs on the Linux MPU

* No button — the loop you used in the Local STT lesson is back, but now each cycle ends with an **action**. Listen for 4 seconds, recognize, act, confirm, repeat.
* ``COMMANDS`` maps phrases directly to **action functions** (``move_left()``, ``take_photo()``, ...). This is one step beyond the earlier pan-tilt lesson, where the table mapped to RPC names — here the table itself carries the function to call, so actions can do several things at once.
* ``take_photo()`` speaks *"Taking a photo."* before capturing, then confirms *"Photo saved."* or *"Failed to save the photo."* — the board reports success or failure out loud.
* TTS feedback runs only after listening has stopped, so the speaker's own voice is never picked up as a new command.
* Every cycle is wrapped in ``try/except`` — if anything fails, the board prints the error, waits 2 seconds, and keeps going. One bad cycle never kills the app.

**Sketch (sketch.ino)** — runs on the STM32 MCU

The sketch is the same five servo RPCs from the pan-tilt lesson: ``pan_left``, ``pan_right``, ``tilt_up``, ``tilt_down``, and ``center`` — with the pan servo on D9 and the tilt servo on D10. The camera runs entirely on the Python side, so the sketch doesn't know anything about photos.

* The sketch drives the servos with the ``Arduino_HardwareServo`` library — the UNO Q uses the STM32's hardware PWM, because the standard Servo library causes jitter on this board.

3. Experiment
----------------

**Try Every Command**

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - You say
     - Expected result
   * - "Take photo"
     - Photo saved as ``photos/photo_001.jpg``; speaker says *"Taking a photo."* then *"Photo saved."*
   * - "Turn left"
     - Pan turns left; speaker says *"Turning left."*
   * - "Look up"
     - Tilt looks up; speaker says *"Looking up."*
   * - "Center"
     - Both servos return to the **90°** center; speaker says *"Returning to center."*
   * - "Play music"
     - Nothing happens; speaker says *"Command not recognized."*

**Change the Listening Cycle**

``LISTEN_SECONDS = 4`` controls how long each cycle records:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Value
     - Effect
   * - ``2``
     - Snappier cycles — good for single-word commands
   * - ``4``
     - Default — comfortable for short phrases
   * - ``8``
     - More time to finish a long command, but responds slower

4. Troubleshooting
--------------------

**The servos move but the camera doesn't work — or the other way around**

* **Cause:** The Robot Shield has no external power, or the Multimedia Carrier isn't firmly attached.
* **Solution:** Check that external power is connected to the Robot Shield, and that the Carrier is firmly connected to the UNO Q. Stop and run the app again.

**The board keeps saying "Command not recognized."**

* **Cause:** The recognized text doesn't contain any phrase from the ``COMMANDS`` table.
* **Solution:** Use the exact phrases: turn left, turn right, look up, look down, center, take photo. Short forms like "left" and "up" also work. Speak after the prompt **Listening... Please speak.** appears.

**The speaker's reply starts a new, wrong command**

* **Cause:** The microphone is listening while the speaker plays.
* **Solution:** Make sure the next ``stt.start_listening()`` runs only after the action and the ``PAUSE_BETWEEN_CYCLES`` wait — the code never records during TTS playback.

**The photo is upside down**

* **Cause:** The ``cv2.flip(frame, 0)`` line is missing or commented out.
* **Solution:** Make sure the flip runs before ``cv2.imwrite()`` — the camera sits upside down on the pan-tilt mount.

**A cycle prints "Voice-control cycle error"**

* **Cause:** Something failed in one cycle — a noisy recording or a busy device — but the app recovered and continued.
* **Solution:** Nothing to fix. This is the safety net working: the error is printed, the app waits 2 seconds, and the next cycle starts fresh.

5. Summary
-------------

You've built a voice-controlled robot assistant! In this lesson, you learned:

* How a continuous listen-recognize-act loop works without a button
* How a ``COMMANDS`` table maps phrases directly to action functions
* How to combine camera, servos, STT, and TTS in one app
* How ``try/except`` keeps the app alive through individual failures

In the next module, your UNO Q will connect to the web — you'll build interfaces that control hardware from a browser and dashboards that show live sensor data.
