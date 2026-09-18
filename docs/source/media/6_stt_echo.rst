.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

06 STT Echo
=============

You've made the board speak (TTS) and made it listen (STT). Now you'll close the loop: hold the button, say a sentence, release it — the board recognizes your speech and repeats it aloud through the speaker. Your own words travel in through the microphone and back out through the speaker.

In this lesson, you will learn to:

* Combine the ``sunfounder_stt`` and ``sunfounder_tts`` Bricks in one app
* Pass the recognized text to the TTS engine with ``tts.say()``
* Keep the microphone off while the speaker plays so the board never hears itself

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

This project uses the following App Lab Bricks:

* Bricks:

  * ``sunfounder_stt`` (local speech-to-text, Whisper model)
  * ``sunfounder_tts`` (local text-to-speech, EdgeTTS engine)

.. note::

   The project ZIP is large (about 100 MB) because it bundles the local speech recognition model. The first import takes a while — this is normal.

**Wiring Diagram**

Connect the push button between D4 and GND — no external resistor is needed, the sketch uses the internal pull-up resistor. The speaker and microphone are built into the Multimedia Carrier.

.. image:: /img/wiring/wiring_button.png
   :width: 500
   :align: center

2. Run the App
----------------

#. Download :download:`06 STT Echo.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/06.STT.Echo.zip>` and import it in **Arduino App Lab**.

#. Click **Run** (▶). The Output window shows:

   *"STT Echo is ready."*

#. Hold the button, say a sentence — for example, "Hello Arduino" — then release the button. The board prints **You said: hello arduino** and the speaker repeats the sentence aloud.

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
       P->>P: stt.get_result() → "Hello Arduino"
       P->>P: print(f"You said: ...")
       P->>P: tts.say(text)
       Note over P: speaker plays — recording stays off

* This lesson combines the two Bricks you already know: STT turns your speech into text, and TTS turns that text back into speech. The same ``text`` variable is printed and spoken.
* ``tts.say()`` blocks — Python waits until the speech finishes before continuing. During that time ``recording`` is ``False``, so the microphone is not recording while the speaker plays. The board never picks up its own reply and re-recognizes it in a loop.
* If the recognition result is empty (silence or noise), the code prints **No speech detected.** instead of speaking.

3. Experiment
----------------

**Change the Echo Volume**

``tts.set_volume(50)`` controls how loud the echo plays:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Value
     - Effect
   * - ``30``
     - A quiet echo — good for a desk in a quiet room
   * - ``50``
     - Default — comfortable for most situations
   * - ``80``
     - A loud echo — fills the room

**Change the Echo Voice**

Try a different voice character in ``set_voice()``:

.. code-block:: python

   tts.set_voice("en-GB-SoniaNeural")   # British English female

Now the board repeats your words with a British accent.

**Challenge: Change the Reply**

The board currently echoes your exact words. Make it answer like a robot instead — keep ``print(f"You said: {text}")``, but change what it speaks:

.. code-block:: python

   tts.say("You said " + text + ". That's interesting!")

Now the board comments on what you said instead of just repeating it.

4. Troubleshooting
--------------------

**The speaker stays silent after recognition**

* **Cause:** The TTS runtime is still being set up on the first run, or the audio environment isn't configured.
* **Solution:** The first run can take half an hour or more while App Lab downloads the TTS runtime — keep the UNO Q connected to the Internet and wait. Check that the Multimedia Carrier is firmly attached to the UNO Q.

**"You said:" appears, but the spoken echo sounds different**

* **Cause:** The local model misheard you, and TTS speaks exactly what was recognized — mistakes and all.
* **Solution:** Speak clearly and reduce background noise. Short, common sentences work best with the small local model.

**The board echoes its own reply in a loop**

* **Cause:** The microphone is recording while the speaker plays.
* **Solution:** Make sure the code keeps ``recording = False`` until the button is pressed again — ``tts.say()`` blocks inside the released branch, so the next recording only starts on the next button press.

**"No speech detected." appears for every try**

* **Cause:** The microphone isn't picking up your voice, or the room is too quiet.
* **Solution:** Speak closer to the microphone and a bit louder. Check that the Multimedia Carrier is firmly attached. Say a full sentence instead of a single word.

5. Summary
-------------

The board heard you and answered back — the speech loop is closed! In this lesson, you learned:

* How to combine the STT and TTS Bricks in a single app
* How the recognized text flows from ``get_result()`` into ``tts.say()``
* Why the microphone stays off while the speaker plays

In the next lesson, your voice commands will move physical hardware — a two-servo pan-tilt.
