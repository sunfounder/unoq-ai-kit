.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

01 Local TTS
===============

In Module A, your output devices were LEDs, buzzers, and servos — they communicated through light, sound, and motion. Now you'll use the Multimedia Carrier's built-in **speaker** — it can speak real sentences. This project is simple: make the speaker say one sentence.

In this lesson, you will learn to:

* Use the ``EdgeTTS`` engine to convert text into speech
* Select different voice characters
* Control the speaker volume with ``gain``

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

.. note::

   No breadboard, no resistors, no jumper wires. The speaker is built into the Multimedia Carrier.

**Software Requirements**

This project uses the following App Lab Bricks and libraries:

* Bricks:

  * ``robot_shield`` (Robot Shield hardware access)
  * ``sunfounder_tts`` (EdgeTTS engine)

2. Code
----------

**Import and Run the Code**

All code for this course is provided as ``.zip`` files that you can import directly into App Lab.

#. Open **Arduino App Lab**, import ``01 Local TTS.zip`` from the ``unoq-ai-kit/media/`` folder.

#. Click **Run** (▶). The speaker says:

   *"Hello! Welcome to Arduino App Lab."*

**The Code**

.. code-block:: python
   :linenos:

   from arduino.app_utils import App
   from sunfounder_tts import EdgeTTS

   tts = EdgeTTS(gain=0.4)
   tts.set_voice("en-US-JennyNeural")

   print("Speaking...")
   tts.say("Hello! Welcome to Arduino App Lab.")
   print("Done.")

   def loop():
       time.sleep(10)

   App.run(user_loop=loop)

**How it Works**

.. code-block:: text

   EdgeTTS(gain=0.4)      → create the TTS engine at 40% volume
   tts.set_voice(...)      → choose a voice character
   tts.say(text)           → convert text to speech and play

* ``EdgeTTS`` is a text-to-speech engine that runs locally — it downloads voice models on first use but does not need the internet to play.
* ``gain=0.4`` controls the volume, from 0.0 (silent) to 1.0 (maximum).
* ``set_voice("en-US-JennyNeural")`` chooses an American English female voice. You can change this to ``en-US-GuyNeural`` (male) or other voices.
* ``App.run(user_loop=loop)`` keeps the Python app alive after the speech finishes.

3. Experiment
----------------

**Change the Text**

Edit the text string in ``tts.say()`` to make the speaker say something different:

.. code-block:: python

   tts.say("Hello, SunFounder!")

Run again — the speaker says the new text.

**Change the Voice**

Try different voice characters:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Voice Code
     - Effect
   * - ``en-US-JennyNeural``
     - American English female (default)
   * - ``en-US-GuyNeural``
     - American English male
   * - ``en-GB-SoniaNeural``
     - British English female
   * - ``en-AU-NatashaNeural``
     - Australian English female

**Challenge: Adjust the Volume**

Change ``gain`` from 0.4 to 0.8, then to 0.1. Find the volume that sounds most comfortable to you.

4. Troubleshooting
--------------------

**No sound at all**

* **Cause:** The speaker environment isn't configured, or the Multimedia Carrier isn't properly attached.
* **Solution:** Run ``./docker-img-make`` in the terminal. Check that the Carrier is firmly connected to the UNO Q.

**Program ends immediately with no sound**

* **Cause:** ``tts.say()`` may need a few seconds to download the voice model on first run.
* **Solution:** Wait 5–10 seconds. If there is still no sound, check your internet connection — the first run downloads the model.

**Sound is too quiet**

* **Cause:** The ``gain`` value is too low.
* **Solution:** Increase ``gain`` from 0.4 to 0.6 or 0.8.

5. Summary
-------------

You've made the UNO Q speak real sentences! In this lesson, you learned:

* How to create a TTS engine with ``EdgeTTS``
* How to choose a voice character with ``set_voice()``
* How to control volume with ``gain``

In the next lesson, you'll make the speaker say dynamic content — sensor readings and changing data, not just a fixed sentence.
