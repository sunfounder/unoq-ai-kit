.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

01 Local TTS
===============

In Module A, your output devices were LEDs, buzzers, and servos — they communicated through light, sound, and motion. Now you'll use the Multimedia Carrier's built-in **speaker** — it can speak real sentences. This project is simple: make the speaker say one sentence.

In this lesson, you will learn to:

* Use the ``EdgeTTS`` engine to convert text into speech
* Select different voice characters
* Control the speaker volume with ``set_volume()``

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

  * ``sunfounder_tts`` (EdgeTTS engine)

2. Run the App
----------------

#. Download :download:`01 Local TTS.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/01.Local.TTS.zip>`.
#. In App Lab, go to **Apps** → **Create new app** → **Import App** → **Import from Computer**, and open the package you downloaded.
#. Click **Run** (▶). The speaker says:

   *"Hello! Welcome to Arduino App Lab."*

.. note::

   The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

**How it Works**

.. code-block:: text

   EdgeTTS()                → create the TTS engine
   tts.set_voice(...)      → choose a voice character
   tts.set_volume(50)      → set the speaker volume (default 50)
   tts.say(text)           → convert text to speech and play

* ``EdgeTTS`` is a text-to-speech engine that runs locally — it downloads voice models on first use but does not need the internet to play.
* ``set_voice("en-US-JennyNeural")`` chooses an American English female voice. You can change this to ``en-US-GuyNeural`` (male) or other voices.
* ``set_volume(50)`` sets the speaker volume from 0 to 100. The default is 50 — a comfortable range is 30 to 100.
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

**Change the Volume**

``set_volume()`` accepts a value from 0 (silent) to 100 (loudest):

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Value
     - Effect
   * - ``30``
     - Quiet — good for a desk in a quiet room
   * - ``50``
     - Default — comfortable for most situations
   * - ``80``
     - Loud — fills a room

**Challenge: Speak a Conversation**

Make the speaker say three sentences in a row — a greeting, a question, and an answer:

.. code-block:: python

   tts.say("Hello! Welcome to Arduino App Lab.")
   tts.say("How are you today?")
   tts.say("I hope you enjoy building with the UNO Q.")

4. Troubleshooting
--------------------

**No sound at all**

* **Cause:** The Multimedia Carrier isn't properly attached, or the volume is set too low.
* **Solution:** Check that the Carrier is firmly connected to the UNO Q. Make sure ``set_volume()`` hasn't been set to a very low value — 30 to 100 is a comfortable range.

**Program ends immediately with no sound**

* **Cause:** The TTS runtime is still being set up on first run.
* **Solution:** The first run can take half an hour or more while App Lab downloads the TTS runtime and audio dependencies — keep the UNO Q connected to the Internet and wait for the setup to finish. This setup only happens once; later runs start much faster.

**The voice sounds robotic or mispronounces words**

* **Cause:** The chosen voice character doesn't fit the text, or the text contains unusual words.
* **Solution:** Try a different voice from the Experiment section. Keep sentences short and simple — local TTS engines handle common words best.

5. Summary
-------------

You've made the UNO Q speak real sentences! In this lesson, you learned:

* How to create a TTS engine with ``EdgeTTS``
* How to choose a voice character with ``set_voice()``
* How to control the speaker volume with ``set_volume()``

In the next lesson, you'll make the speaker say dynamic content — sensor readings and changing data, not just a fixed sentence.
