.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

03 Voice Recorder
====================

The board has been talking — now you'll speak to it. In this lesson, the UNO Q becomes a **dictaphone**: press one button to record your voice, press it again to save, then press the other button to play the recording back through the speaker. No speech recognition yet — just capture and playback.

In this lesson, you will learn to:

* Record audio from the microphone with the STT Brick's recording API
* Play a saved audio file through the speaker with the TTS Brick
* Read two buttons at once and use them as toggle switches
* Keep recording and playback from running at the same time

1. Setup
----------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 2 * :ref:`cpn_button`
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

This project uses the following App Lab Bricks:

* Bricks:

  * ``sunfounder_stt`` (microphone recording — only the recording API, no speech recognition in this lesson)
  * ``sunfounder_tts`` (speaker playback — only the playback API, no text synthesis in this lesson)

**Wiring Diagram**

Connect the two push buttons between D7 / D6 and GND — no external resistors are needed, the sketch uses the internal pull-up resistors. The microphone and speaker are built into the Multimedia Carrier.

- Record button: pin 1 → **D7**, pin 2 → **GND**
- Play button: pin 1 → **D6**, pin 2 → **GND**

.. image:: /img/wiring/wiring_two_buttons.png
   :width: 500
   :align: center

2. Run the App
----------------

#. Download :download:`03 Voice Recorder.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/03.Voice.Recorder.zip>` and import it in **Arduino App Lab**.

#. Click **Run** (▶). The Output window shows::

      === Voice Recorder ===
      D7: Record / Stop Recording
      D6: Play / Stop Playback
      Ready.

#. Press the **D7 button** once — **Recording...** appears in the Output window. Say something into the microphone.

#. Press **D7** again — **Recording saved.** appears.

#. Press the **D6 button** once — **Playing...** appears and the speaker plays your recording. Press **D6** again to stop playback.

.. note::

   The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

**How it Works**

.. mermaid::

   sequenceDiagram
       participant B1 as Record Button (D7)
       participant B2 as Play Button (D6)
       participant S as Sketch (sketch.ino)
       participant P as Python (main.py)

       loop every 0.05 s
           P->>S: Bridge.call("record_button_read")
           P->>S: Bridge.call("play_button_read")
           S-->>P: 0 or 1 for each button
       end
       Note over P: D7 press edge (not recording)
       P->>P: tts.stop_audio() first
       P->>P: stt.start_recording()
       Note over P: D7 press edge again
       P->>P: stt.stop_recording(AUDIO_FILE)
       Note over P: D6 press edge
       P->>P: tts.play_audio(AUDIO_FILE)
       Note over P: D6 press edge again
       P->>P: tts.stop_audio()

**Sketch (sketch.ino)** — runs on the STM32 MCU

The sketch reads both buttons and registers two RPC functions:

.. code-block:: cpp

   int recordButtonRead(String dummy)
   {
       (void)dummy;
       return digitalRead(RECORD_BUTTON_PIN) == LOW ? 1 : 0;
   }

   Bridge.provide("record_button_read", recordButtonRead);
   Bridge.provide("play_button_read", playButtonRead);

* ``RECORD_BUTTON_PIN = 7`` and ``PLAY_BUTTON_PIN = 6`` both use ``INPUT_PULLUP`` — pressing a button connects its pin to GND and the function returns ``1``.
* Two Bridge RPCs are registered, one per button. Python polls both about 20 times per second.

**Python (main.py)** — runs on the Linux MPU

* The **STT Brick is used only for recording** here — ``stt.start_recording()`` opens the microphone and ``stt.stop_recording(AUDIO_FILE)`` saves the captured audio as a WAV file. No speech recognition runs in this lesson.
* The **TTS Brick is used only for playback** — ``tts.play_audio(AUDIO_FILE)`` sends the saved file to the speaker, and ``tts.stop_audio()`` stops it. No text synthesis runs.
* Each button is a **toggle**: Python compares every reading with the previous one, so one press starts the action and the next press stops it.
* Recording and playback never overlap — starting a recording stops any playback first, and pressing Play while recording only prints a reminder: **Stop recording before playback.**

3. Experiment
----------------

**Record a Longer Message**

Record a few different clips and play them back one by one:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - You do
     - Expected result
   * - Press D7, count to three out loud, press D7
     - **Recording saved.** — the clip is stored
   * - Press D6
     - **Playing...** — the speaker plays your count
   * - Press D6 while playing
     - **Playback stopped.** — the speaker stops immediately
   * - Press D6 again
     - The same clip plays again — it is kept until the next recording

**Record While Playing**

Press D6 to play a clip, then press D7 while it plays — the playback stops and a new recording starts. The app never records and plays at the same time.

**Challenge: Change the Audio File Name**

The recording is always saved to the same file, ``stt_last.wav`` — each new recording replaces the previous one. Change the ``AUDIO_FILE`` path in ``main.py`` to a new name such as ``/app/audio_output/stt_note.wav`` and run again — recordings now save under the new name.

4. Troubleshooting
--------------------

**"Recording..." appears but the recording is silent when played back**

* **Cause:** The microphone wasn't picked up, or the recording was too short.
* **Solution:** Speak closer to the microphone and a bit louder, and record for at least a second. Check that the Multimedia Carrier is firmly attached.

**"Playing..." appears but no sound comes out**

* **Cause:** The TTS runtime is still being prepared on the first run.
* **Solution:** The first run can take half an hour or more while App Lab downloads the TTS runtime — keep the UNO Q connected to the Internet and wait. Check that the Multimedia Carrier is firmly attached to the UNO Q.

**The buttons do nothing when pressed**

* **Cause:** The buttons are wired to the wrong pins.
* **Solution:** Check the Record button connects D7 to GND and the Play button connects D6 to GND — one pin of each button on the digital pin, the other on GND.

**Pressing D6 prints "No recording yet. Press D7 to record first."**

* **Cause:** No recording has been saved in this run.
* **Solution:** Press D7 to record first — the playback button only works after a recording is saved.

5. Summary
-------------

You've built a voice recorder! In this lesson, you learned:

* How to record audio with the STT Brick's ``start_recording()`` / ``stop_recording()``
* How to play a saved WAV file with the TTS Brick's ``play_audio()`` / ``stop_audio()``
* How to read two buttons and use them as toggles
* How to keep recording and playback from overlapping

In the next lesson, the board stops just recording — it will transcribe your speech into text.
