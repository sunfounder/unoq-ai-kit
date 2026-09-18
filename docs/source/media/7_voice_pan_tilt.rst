.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

07 Voice-Controlled Pan-Tilt
==============================

Earlier, you swept servos with the ``Arduino_HardwareServo`` library — now your voice will aim them. Say "Turn left", and the pan-tilt turns left while the speaker confirms *"Turning left."* Speech moves motors, and the board talks back to confirm what it did.

In this lesson, you will learn to:

* Map voice phrases to actions with a ``COMMANDS`` table
* Match recognized text against multiple phrases with ``match_command()``
* Move two servos to fixed angles through Bridge RPCs
* Confirm each action with spoken feedback

1. Setup
----------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_button`
     - 1 * :ref:`cpn_breadboard`
     - Several :ref:`cpn_wires`
   * - |list_pan_tilt|
     - |list_button|
     - |list_breadboard|
     - |list_wire|
   * - 1 * USB Cable
     - -
     - -
     - -
   * - |list_usb_cable|
     - -
     - -
     - -

**Software Requirements**

This project uses the following App Lab Bricks and libraries:

* Bricks:

  * ``sunfounder_stt`` (local speech-to-text, Whisper model)
  * ``sunfounder_tts`` (local text-to-speech, EdgeTTS engine)

* Libraries:

  * ``Arduino_HardwareServo`` (drives the two servo motors)

.. note::

   The project ZIP is large (about 100 MB) because it bundles the local speech recognition model. The first import takes a while — this is normal.

**Wiring Diagram**

Connect the servos to the Robot Shield and the push button to the UNO Q — no external resistor is needed for the button, the sketch uses the internal pull-up resistor:

- Pan servo → **D9**
- Tilt servo → **D10**
- Button pin 1 → **D4**
- Button pin 2 → **GND**

.. image:: /img/wiring/wiring_pan_tilt_button.png
   :width: 500
   :align: center

2. Run the App
----------------

#. Download :download:`07 Voice-Controlled Pan-Tilt.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/07.Voice-Controlled.Pan-Tilt.zip>` and import it in **Arduino App Lab**.

#. Click **Run** (▶). The Output window shows:

   *"Voice-controlled pan-tilt is ready."*

#. Hold the button, say a command — for example, "Turn left" — then release the button. The pan-tilt turns left, the Output window shows **Turning left.**, and the speaker confirms: *"Turning left."*

.. note::

   The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

**How it Works**

.. mermaid::

   sequenceDiagram
       participant B as Button (D4)
       participant S as Sketch (sketch.ino)
       participant P as Python (main.py)

       Note over P: press edge → stt.start_listening()
       Note over P: release edge → stt.stop_listening()
       P->>P: stt.get_result() → "turn left"
       P->>P: match_command() looks up COMMANDS
       P->>P: ("pan_left", "Turning left.", "Turning left.")
       P->>S: Bridge.call("pan_left", "")
       S->>S: panServo.write(135)
       P->>P: print("Turning left.")
       P->>P: tts.say("Turning left.")

**Python (main.py)** — runs on the Linux MPU

* The ``COMMANDS`` table maps each voice phrase to three things: the **Bridge RPC** to call, the **spoken feedback**, and the **console message**. One table drives everything — to add a new command, you add one row.
* ``match_command()`` normalizes the text (lowercase, single spaces) and checks every phrase in the table. Full sentences and short forms both match — "turn left", "look left", and just "left" all trigger the same action.
* If nothing matches, the board says *"Command not recognized."* instead of doing nothing silently.
* The action order matters: the servo moves **first** (``Bridge.call``), then the speaker confirms — the board reports what it already did.

**Sketch (sketch.ino)** — runs on the STM32 MCU

The sketch owns the servo angles. Each Bridge function moves a servo to a fixed absolute angle:

.. code-block:: cpp

   int panLeft(String dummy)
   {
       (void)dummy;
       panServo.write(LEFT_ANGLE);   // 135
       return LEFT_ANGLE;
   }

* ``panServo.attach(9)`` and ``tiltServo.attach(10)`` connect the two servos to D9 and D10 on the Robot Shield.
* The sketch uses the ``Arduino_HardwareServo`` library — the UNO Q drives the servos with the STM32's hardware PWM, because the standard Servo library causes jitter on this board.
* ``LEFT_ANGLE = 135`` is the **absolute** servo angle — no offset math, the value goes straight into ``write()``. The center is ``CENTER_ANGLE = 90``.
* Five RPCs are registered: ``pan_left``, ``pan_right``, ``tilt_up``, ``tilt_down``, and ``center`` — plus ``button_read`` from the earlier lessons.

3. Experiment
----------------

**Try Every Command**

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - You say
     - Expected result
   * - "Turn left"
     - Pan turns left; Output shows ``Turning left.``; speaker says *"Turning left."*
   * - "Look up"
     - Tilt looks up; Output shows ``Looking up.``; speaker says *"Looking up."*
   * - "Center" (or "return to center")
     - Both servos return to the 90° center; speaker says *"Returning to center."*
   * - "Go sideways"
     - Nothing moves; speaker says *"Command not recognized."*

**Change the Movement Angle**

In ``sketch.ino``, make the turns smaller and gentler:

.. code-block:: cpp

   const int LEFT_ANGLE = 120;
   const int RIGHT_ANGLE = 60;

The same voice commands now move the pan-tilt through a narrower sweep.

**Challenge: Change the Spoken Feedback**

The sketch angles and the spoken feedback live in different places — the feedback is the third column of each ``COMMANDS`` row in ``main.py``. Change the feedback text so the board speaks a different confirmation, for example make "Turn left" answer *"Moving left."* instead of *"Turning left."* — without touching the sketch at all.

4. Troubleshooting
--------------------

**The servos don't move at all**

* **Cause:** The servos are plugged into the wrong header, or the Robot Shield has no external power.
* **Solution:** Check the wiring first — the pan servo goes on D9, the tilt servo on D10, and the button connects D4 to GND. Then check that external power is connected to the Robot Shield — the servos draw power from it.

**The servo moves in the wrong direction**

* **Cause:** The servo plug is reversed, or the pan and tilt servos are swapped.
* **Solution:** Swap the two servo plugs on the Robot Shield. The angles are absolute, so a reversed plug flips every direction.

**The board always says "Command not recognized."**

* **Cause:** The recognized text doesn't contain any phrase from the ``COMMANDS`` table.
* **Solution:** Use the exact phrases: turn left, turn right, look up, look down, center. Short forms like "left" and "up" also work — but "go sideways" doesn't.

5. Summary
-------------

Your voice aims the pan-tilt! In this lesson, you learned:

* How a ``COMMANDS`` table maps phrases to RPCs, feedback, and console messages
* How ``match_command()`` finds the right row for the recognized text
* How the sketch moves two servos to fixed absolute angles
* How spoken feedback confirms each action

In the next lesson, the camera gets its turn — one button press, one photo.
