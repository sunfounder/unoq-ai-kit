.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

04 Local STT
===============

In the previous lesson, the UNO Q recorded your voice and played it back — but it didn't understand a word. Now it will **transcribe** your speech: using the AVIO Carrier's built-in microphone and a local speech-to-text engine, the board listens to your voice and prints what you said. Everything runs on the device — no cloud, no internet needed for recognition.

In this lesson, you will learn to:

* Use the ``sunfounder_stt`` Brick to turn speech into text
* Start and stop microphone listening with ``start_listening()`` / ``stop_listening()``
* Read recognition results with ``get_result()``
* Run a background worker thread so the app keeps looping while listening

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

This project uses the following App Lab Brick:

* Bricks:

  * ``sunfounder_stt`` (local speech-to-text, Whisper model)

.. note::

   The project ZIP is large (about 100 MB) because it bundles the local speech recognition model. The first import takes a while — this is normal.

2. Run the App
----------------

#. Download :download:`04 Local STT.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/04.Local.STT.zip>`.
#. In App Lab, go to **Apps** → **Create new app** → **Import App** → **Import from Computer**, and open the package you downloaded.
#. Click the **Run** button (▶). The Output window shows:

   *"Local STT is ready. The microphone will listen for 5 seconds each time."*

#. When you see **Listening... Please speak.**, say something — for example, "Hello Arduino". After 5 seconds the board stops recording, recognizes your speech locally, and prints **You said: hello arduino**. If you stay silent, it prints **No speech detected.** — then the cycle repeats.

**How it Works**

.. code-block:: text

   STT(type="local_fast", language="en") → create the STT engine
   stt.reset()                          → clear the previous result
   stt.start_listening()                → microphone starts recording
   time.sleep(5)                        → record for 5 seconds
   stt.stop_listening()                 → microphone stops
   stt.get_result(timeout=60)           → transcribe and return the text
   (repeat forever)

* The ``STT`` Brick runs a local Whisper model (``local_fast``) — the audio never leaves the board.
* ``get_result()`` returns the recognition result as a dictionary: ``{"text": "...", "status": "..."}``. The code checks with ``isinstance(text, dict)`` and reads the ``"text"`` field, then strips whitespace.
* The whole listening loop runs in a **background thread** (``threading.Thread(...).start()``), so the main program stays responsive.
* Each cycle records for ``LISTEN_SECONDS`` (5 s) — change this constant to listen longer or shorter.

3. Experiment
----------------

**Change the Listening Duration**

Edit ``LISTEN_SECONDS`` at the top of ``main.py``:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Value
     - Effect
   * - ``3``
     - Shorter clips — snappier cycles, works for single words
   * - ``5``
     - Default — comfortable for a short sentence
   * - ``10``
     - Long clips — better for long sentences, slower to respond

**Challenge: Speak Another Language**

Change the ``language`` parameter in ``STT(type="local_fast", language="en")``. Try ``"zh"`` for Chinese or ``"es"`` for Spanish, then speak in that language — the board prints what you said in the language it heard.

4. Troubleshooting
--------------------

**"Loading the local STT model..." takes a long time**

* **Cause:** The local Whisper model is loaded into memory on the first run.
* **Solution:** Wait for **Local STT is ready.** to appear — the first load can take a while, and later restarts are faster.

**It always prints "No speech detected."**

* **Cause:** The microphone isn't picking up your voice, or the room is too quiet.
* **Solution:** Speak closer to the microphone and a bit louder. Check that the AVIO Carrier is firmly attached. Try the recording while saying a full sentence instead of a single word.

**It prints a different word from what you said**

* **Cause:** Small local models can mishear, especially with background noise.
* **Solution:** Speak clearly and reduce background noise. Short, common words (like "hello", "test", "light") work best with the small model.

5. Summary
-------------

The UNO Q can now hear you! In this lesson, you learned:

* How to use the ``sunfounder_stt`` Brick to recognize speech locally
* How to control the microphone with ``start_listening()`` and ``stop_listening()``
* How to read the recognition dictionary returned by ``get_result()``
* How to run a repeating listening loop in a background thread

In the next lesson, your words will control hardware — say a color and an RGB LED lights up.
