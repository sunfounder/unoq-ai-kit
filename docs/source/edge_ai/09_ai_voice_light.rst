.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

09 AI Voice Light
==================

Every AI project you have built so far begins the same way: you point the camera at something and the board looks at it. This one never opens the camera at all — it **listens**. Say "Hey Arduino" to an idle board and it answers "I'm here.", dims an RGB LED green, records one spoken command, and turns the light the colour you asked for. No button, no browser, no keyboard — just your voice, a wake word, and a light.

.. image:: img/09_ai_voice_light.png
   :width: 600
   :align: center

In this lesson, you will learn to:

* Build a **two-stage always-listening pipeline**: a small keyword spotter that runs continuously and gates a much heavier speech recogniser
* Run the ``arduino:keyword_spotting`` Brick with the ``keyword-spotting-hey-arduino`` model, and tune what "confident enough" means
* Record one spoken command with the local Whisper model and turn the recognised sentence into a colour over Bridge
* Put the board's microphone into a known-good state before your model ever starts listening

1. Setup
----------

**What You Need**

.. list-table::
   :widths: 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_rgb_led` (common cathode)
   * - |list_pan_tilt|
     - |list_rgb_led|
   * - 3 * :ref:`cpn_resistor` (220Ω)
     - 1 * USB-C Cable
   * - |list_220ohm|
     - |list_usb_cable|

**Software Requirements**

This project uses three App Lab Bricks:

* Bricks (declared in ``app.yaml``):

  * ``arduino:keyword_spotting`` with ``model: keyword-spotting-hey-arduino`` — the always-on wake-word model. It must be the **first** Brick in the list: declared after another audio Brick it takes over the Web UI port (4912) and the app misbehaves, which is why the shipped ``app.yaml`` carries a comment saying so.
  * ``sunfounder_stt`` — local speech-to-text (Whisper model) for the spoken command
  * ``sunfounder_tts`` — text-to-speech (EdgeTTS) for the assistant's reply

There are no sketch libraries to install: ``sketch.ino`` only includes ``Arduino_RouterBridge``, which ships with the board.

**Wiring Diagram**

The RGB LED has four legs: the longest one is the **common cathode**, and it goes to **GND**. The other three are the red, green, and blue channels — **R** to **D8**, **G** to **D7**, and **B** to **D6**, each through its own 220Ω resistor so the LED cannot burn out.

.. image:: /img/wiring/wiring_rgb_led.png
   :width: 500
   :align: center

.. note::

   This project listens through the **microphone** and answers through the **speaker** — both are built into the Multimedia Carrier, so there is nothing extra to plug in. Keep the board connected to the Internet: the ``EdgeTTS`` engine fetches its voice data the first time it speaks.

   The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

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

#. Navigate to the ``unoq-ai-kit/edge_ai/`` folder and select ``09 AI Voice Light.zip``.

#. The app appears in **Apps** — click it to open.

**Run the Code**

#. Click the **Run** button (▶).

   .. image:: /img/app_run.png
      :width: 500
      :align: center

   There is no Web UI tab in this project — **the Python console is the entire interface**. Startup prints one line per stage, in order:

   * ``[MIC] Capture route and gain applied (ADC2 Volume=8, TX_DEC0 Volume=100).``
   * ``[STARTING] Opening the keyword spotting model...`` then ``[OK] Keyword spotting running for "Hey Arduino" (wake threshold 0.45).``
   * ``[STARTING] Loading speech recognition for commands...`` then ``[OK] Speech recognition loaded.``
   * ``[STARTING] Initializing text to speech...`` then ``[OK] Text to speech ready.``

   The speech-recognition step is the slow one, because the local Whisper model has to be loaded into memory before the app can hear anything.

#. Wait for the startup to finish. The app announces that it is ready with a short banner that starts ``Say "Hey Arduino". The model prints its opinion for every window`` and then lists what the three possible keywords mean. From that moment the board is listening.

   Right after that you will also see ``[READY] Waiting for "Hey Arduino"...`` — that is the line the app prints every time it finishes an interaction and returns to standby, including the first one. If you like a periodic "I am alive" signal instead, the heartbeat gives you one every 15 seconds::

      [LISTENING] Microphone active. wakes=0, last wake 15s ago.

#. Say **"Hey Arduino"** clearly, from about an arm's length away. Because debug logging is switched on, the model reports what it thought of every one-second window it examined — lines like these appear continuously, whether or not you are talking::

      Keyword 'background' detected with confidence 100.00%.
      Keyword 'other' detected with confidence 99.11%.
      Keyword 'hey_arduino' detected with confidence 99.97%.

   When a window clears the threshold you get the wake sequence::

      [WAKE] "Hey Arduino" recognised - waking up.
      [TTS] I'm here.

   The speaker says "I'm here." and the RGB LED glows a **dim green** — a silent, visual "I'm listening" for anyone who cannot hear the speaker.

#. Speak your command **as soon as "I'm here." finishes**, for example *"Turn the light blue."* The console shows::

      [LISTENING] Speak your command now...
      [HEARD] turn the light blue.
      [ACTION] Light is now blue.
      [READY] Waiting for "Hey Arduino"...

   The LED flashes the new colour as the command is executed, then goes dark as the app returns to standby. If the sentence contained no colour it recognises, ``[ACTION]`` says so instead — the light stays off but everything else keeps working.

#. Try the other presets — red, green, blue, yellow, purple, white — and *"Turn the light off."* Then simply stop talking: the heartbeat keeps printing every 15 seconds, proving the microphone and the model are still running while they wait for the next wake word.

**The Code**

**Python (python/main.py)** — runs on the Linux MPU: keyword spotting, speech recognition, and speech

.. code-block:: python
   :linenos:

   """AI Voice Light: Edge AI keyword spotting.

   Behaviour
   ---------
   The keyword spotting model classifies one second of microphone audio at a
   time into ``background``, ``hey_arduino`` or ``other``. When the
   ``hey_arduino`` score clears CONFIDENCE the assistant wakes: it answers
   "I'm here.", records one spoken command, prints what it heard, changes the
   RGB LED, then goes back to waiting.

   Seeing what the model thinks
   ----------------------------
   The brick stays completely silent when a window does not clear the threshold,
   which makes a working app look broken. Debug logging for the audio module is
   switched on below, exactly as Arduino's own support guidance describes. With
   it on, the library prints the winning class and its confidence for the windows
   it evaluates:

       Keyword 'background' detected with confidence 100.00%.
       Keyword 'other' detected with confidence 99.11%.
       Keyword 'hey_arduino' detected with confidence 99.97%.

   If you only ever see 'background' while you say the wake word, the model does
   not match your pronunciation. Raise or lower CONFIDENCE, or train your own
   model on Edge Impulse with your own recordings - the model shipped with the
   board was trained on a single speaker's voice.

   Do NOT wrap KeywordSpotting.infer_from_features to read the raw scores. That
   stops the brick's inference loop from running at all (observed: zero windows
   evaluated, microphone never opened), and running two KeywordSpotting instances
   to get a second threshold does the same thing. Debug logging is the supported
   route.
   """

   import logging
   import subprocess
   import threading
   import time

   # Enable the audio module's debug output. This is the documented way to see
   # per-window results, and unlike wrapping the model it does not disturb it.
   from arduino.app_internal.core.audio import logger as _audio_logger

   _audio_logger.setLevel(logging.DEBUG)

   from arduino.app_utils import App, Bridge
   from arduino.app_bricks.keyword_spotting import KeywordSpotting
   from sunfounder_stt import STT
   from sunfounder_tts import EdgeTTS


   # How sure the model has to be before the assistant wakes up. The brick's own
   # default is 0.8. Lower it (0.3 - 0.5) if your pronunciation scores low; raise
   # it if the assistant starts waking on its own.
   CONFIDENCE = 0.45

   # How often to prove that detection is still alive.
   HEARTBEAT_SECONDS = 15.0

   # How long to record the spoken command once awake.
   COMMAND_SECONDS = 4.0

   WAKE_WORD = "hey_arduino"
   WAKE_LABEL = "Hey Arduino"

   COLOR_PRESETS = {
       "red": (255, 0, 0),
       "green": (0, 255, 0),
       "blue": (0, 0, 255),
       "yellow": (255, 255, 0),
       "purple": (160, 32, 240),
       "white": (255, 255, 255),
   }

   stt = None
   tts = None
   spotter = None
   ready = False
   busy = False
   wake_count = 0
   last_wake_at = time.time()
   state_lock = threading.Lock()


   def set_light(red, green, blue):
       """Send one RGB value to the Arduino sketch."""
       Bridge.call("set_rgb", int(red), int(green), int(blue))


   def prepare_microphone():
       """Put the capture route and gain into a known-good state.

       The saved system state leaves the capture gain at its minimum, and a
       speech recognition brick from another app can leave the capture route
       switched off entirely. Either way the model would run happily and hear
       nothing - measured on this kit, normal speech registered RMS 67 with the
       saved gain and RMS 1200 with the values below.
       """
       settings = (
           ("MultiMedia3 Mixer TX_CODEC_DMA_TX_3", "1"),
           ("TX DEC0 MUX", "SWR_MIC"),
           ("TX SMIC MUX0", "SWR_MIC1"),
           ("TX_AIF1_CAP Mixer DEC0", "1"),
           ("ADC2 Switch", "1"),
           ("ADC2 MUX", "INP2"),
           ("ADC2_MIXER Switch", "1"),
           ("ADC2 Volume", "8"),
           ("TX_DEC0 Volume", "100"),
       )
       try:
           for name, value in settings:
               subprocess.run(
                   ["amixer", "-c0", "cset", f"iface=MIXER,name={name}", value],
                   capture_output=True, timeout=10,
               )
           print("[MIC] Capture route and gain applied "
                 "(ADC2 Volume=8, TX_DEC0 Volume=100).", flush=True)
       except Exception as error:
           print(f"[MIC] Could not configure the microphone: "
                 f"{type(error).__name__}: {error}", flush=True)


   def on_wake():
       """The model is sure enough: wake the assistant."""
       global wake_count, last_wake_at
       with state_lock:
           if busy or not ready:
               return
           wake_count += 1
           last_wake_at = time.time()
       threading.Thread(target=handle_command, daemon=True).start()


   def listen_for_command():
       """Wake, record one command, print it, act on it."""
       print("", flush=True)
       print(f'[WAKE] "{WAKE_LABEL}" recognised - waking up.', flush=True)
       try:
           tts.say("I'm here.")
           print("[TTS] I'm here.", flush=True)
       except Exception as error:
           print(f"[TTS] failed: {type(error).__name__}: {error}", flush=True)

       set_light(0, 60, 0)          # visible sign that it is awake
       time.sleep(0.3)

       print("[LISTENING] Speak your command now...", flush=True)
       try:
           stt.reset()
           stt.start_listening()
           time.sleep(COMMAND_SECONDS)
           stt.stop_listening()
           result = stt.get_result(timeout=60)
       except Exception as error:
           print(f"[STT] failed: {type(error).__name__}: {error}", flush=True)
           return

       if isinstance(result, dict):
           result = result.get("text", "")
       heard = str(result).strip() if result else ""

       print(f'[HEARD] {heard if heard else "(nothing recognised)"}', flush=True)
       run_command(heard)


   def run_command(text):
       """Act on a spoken command."""
       command = " ".join(str(text).lower().split())

       for name, color in COLOR_PRESETS.items():
           if name in command:
               set_light(*color)
               print(f"[ACTION] Light is now {name}.", flush=True)
               return

       if "off" in command:
           set_light(0, 0, 0)
           print("[ACTION] Light off.", flush=True)
           return

       if text:
           print("[ACTION] No supported light command in that sentence.",
                 flush=True)


   def handle_command():
       """Run one wake interaction without blocking the detector callback."""
       global busy
       with state_lock:
           if busy:
               return
           busy = True
       try:
           listen_for_command()
       except Exception as error:
           print(f"[ERROR] {type(error).__name__}: {error}", flush=True)
       finally:
           set_light(0, 0, 0)
           busy = False
           print('[READY] Waiting for "Hey Arduino"...', flush=True)


   def heartbeat():
       """Prove the microphone and the model are alive.

       Without this the console goes quiet whenever the wake word is not
       recognised, and a working app is indistinguishable from a dead one.
       """
       while True:
           time.sleep(HEARTBEAT_SECONDS)
           with state_lock:
               wakes = wake_count
               since = time.time() - last_wake_at

           if not ready:
               print("[WAIT] Still starting up...", flush=True)
           elif busy:
               print(f"[BUSY] Handling a command. (wakes={wakes})", flush=True)
           else:
               print(f"[LISTENING] Microphone active. wakes={wakes}, "
                     f"last wake {since:.0f}s ago.", flush=True)


   def initialize():
       """Bring up the microphone, the model, speech recognition and speech."""
       global stt, tts, spotter, ready

       prepare_microphone()

       try:
           print("[STARTING] Opening the keyword spotting model...", flush=True)
           spotter = KeywordSpotting(confidence=CONFIDENCE)
           spotter.on_detect(WAKE_WORD, on_wake)
           print(f"[OK] Keyword spotting running for \"{WAKE_LABEL}\" "
                 f"(wake threshold {CONFIDENCE:.2f}).", flush=True)
       except Exception as error:
           print(f"[STARTUP ERROR] Keyword spotting failed: "
                 f"{type(error).__name__}: {error}", flush=True)
           return

       try:
           print("[STARTING] Loading speech recognition for commands...",
                 flush=True)
           stt = STT(type="local_fast", language="en")
           stt.reset()
           print("[OK] Speech recognition loaded.", flush=True)
       except Exception as error:
           print(f"[STARTUP ERROR] Speech recognition failed: "
                 f"{type(error).__name__}: {error}", flush=True)
           return

       try:
           print("[STARTING] Initializing text to speech...", flush=True)
           tts = EdgeTTS()
           tts.set_voice("en-US-JennyNeural")
           tts.set_volume(50)
           print("[OK] Text to speech ready.", flush=True)
       except Exception as error:
           print(f"[WARN] Text to speech failed, commands still work: "
                 f"{type(error).__name__}: {error}", flush=True)

       set_light(0, 0, 0)
       ready = True
       print("", flush=True)
       print(f'Say "{WAKE_LABEL}". The model prints its opinion for every window',
             flush=True)
       print("it evaluates, so you can see what it made of your pronunciation:",
             flush=True)
       print("  Keyword 'hey_arduino' detected with confidence N%   <- woke up",
             flush=True)
       print("  Keyword 'background' detected ...                    <- it heard",
             flush=True)
       print("                                                         nothing",
             flush=True)
       print("  Keyword 'other' detected ...                         <- speech, ",
             flush=True)
       print("                                                         not the",
             flush=True)
       print("                                                         wake word",
             flush=True)
       print("", flush=True)


   threading.Thread(target=heartbeat, daemon=True).start()
   threading.Thread(target=initialize, daemon=True).start()

   App.run()

**Sketch (sketch/sketch.ino)** — runs on the STM32 MCU: three PWM channels and one Bridge function

.. code-block:: cpp
   :linenos:

   #include <Arduino_RouterBridge.h>

   const int RED_PIN = 8;
   const int GREEN_PIN = 7;
   const int BLUE_PIN = 6;

   void setRgb(int red, int green, int blue)
   {
       analogWrite(RED_PIN, constrain(red, 0, 255));
       analogWrite(GREEN_PIN, constrain(green, 0, 255));
       analogWrite(BLUE_PIN, constrain(blue, 0, 255));
   }

   void setup()
   {
       pinMode(RED_PIN, OUTPUT);
       pinMode(GREEN_PIN, OUTPUT);
       pinMode(BLUE_PIN, OUTPUT);
       setRgb(0, 0, 0);

       Bridge.begin();
       Bridge.provide("set_rgb", setRgb);
   }

   void loop()
   {
       delay(10);
   }

**How it Works**

.. mermaid::

   sequenceDiagram
       participant M as Microphone
       participant K as Keyword spotter Brick
       participant P as Python (main.py)
       participant T as EdgeTTS Brick
       participant L as RGB LED (sketch.ino)

       M->>K: continuous 1-second audio windows
       Note over K: background / other / hey_arduino
       K->>P: on_detect("hey_arduino") above 0.45
       P->>T: tts.say("I'm here.")
       P->>L: Bridge.call("set_rgb", 0, 60, 0) — dim green cue
       P->>P: stt.start_listening() for 4 seconds
       M->>P: 4 s of audio → Whisper → text
       P->>P: run_command(text) matches a colour preset
       P->>L: Bridge.call("set_rgb", r, g, b)
       P->>P: busy = False, back to [READY]

**Two stages, two very different prices.** The microphone is always open, but two models take turns listening to it, and they cost wildly different amounts of work. The keyword spotter looks at one second of audio and answers a single small question — *background*, *other*, or *hey_arduino* — using a tiny model that fits comfortably in memory and finishes in milliseconds. Whisper, the speech recogniser, has to turn a full sentence of arbitrary English into text, which means far more computation per second of audio. Running Whisper continuously would keep the processor busy forever, just to throw almost all of the result away.

So the cheap model gates the expensive one. That gating is the whole idea of this project, and it buys you three things at once. **Privacy:** the board never transcribes the room. Everything the microphone hears outside the four seconds after a wake word is classified and discarded — it is never turned into text and never leaves the board. **CPU:** the heavy recogniser runs for four seconds per command instead of all day, which leaves the processor free for the rest of the app. **Responsiveness:** the keyword spotter is small enough to answer within a second, so the wake word feels instant, while the slow recogniser only has to be fast enough for one short command.

**The keyword spotter — the gate.** ``KeywordSpotting(confidence=CONFIDENCE)`` creates the Brick and ``spotter.on_detect(WAKE_WORD, on_wake)`` registers the callback for the class named ``"hey_arduino"``. ``CONFIDENCE`` is set to ``0.45``, deliberately lower than the Brick's own default of ``0.8``: the smaller the number, the easier it is to wake the assistant, and the more likely it is to wake up on its own. ``on_wake()`` is called from the Brick's own audio thread, so it does almost nothing — it takes a lock, refuses to act if an interaction is already running (``if busy or not ready``) or if the models are not up yet, counts the wake, and hands the real work to a separate thread. That is what keeps the detector listening at full speed while the assistant is busy talking and recording.

**Why you can see the model's opinion at all.** By default the Brick says nothing when a window fails to clear the threshold, and an app that hears nothing looks exactly like an app that is broken. That is why the file sets ``_audio_logger.setLevel(logging.DEBUG)`` — the supported way to make the library print the winning class and its confidence for every window it evaluates. It is also why you should not try to read the raw scores yourself by wrapping ``infer_from_features``: doing that stops the Brick's inference loop entirely, and running a second ``KeywordSpotting`` instance to get a second threshold does the same thing.

**Waking, listening, acting.** Once the gate opens, ``listen_for_command()`` replies through the speaker with ``tts.say("I'm here.")`` — a blocking call, so Python waits for the speech to finish — and lights the LED dim green with ``set_light(0, 60, 0)``. Note the 60: full-strength green would be 255, and a calm cue is friendlier than a glare. Then it resets the recogniser, starts recording, sleeps for ``COMMAND_SECONDS`` (four seconds), stops recording, and asks for the result with ``get_result(timeout=60)``. The spoken sentence comes back as text, is printed as ``[HEARD]``, and goes to ``run_command()``.

**From a sentence to a colour.** ``run_command()`` lower-cases the text and collapses its whitespace, then walks the ``COLOR_PRESETS`` dictionary **in its fixed order** and takes the *first* preset whose name appears anywhere in the sentence. It never parses grammar and it never cares about word order — this is simple substring matching, which is exactly why it works so reliably with a small local model, and exactly why saying two colours in one sentence gives you the one that appears first in the dictionary rather than the one you said first. If no colour matched, it looks for ``"off"``; if that is missing too, it prints the "no supported light command" line. Every match ends in the same place: ``set_light()`` calls ``Bridge.call("set_rgb", r, g, b)``, which crosses the Bridge into the sketch's ``setRgb()``, which clamps each value with ``constrain()`` and writes it to **D8**, **D7**, and **D6** with ``analogWrite()``. After the command finishes, the ``finally`` block clears the LED back to black and prints ``[READY]`` — standby, listening again.

**Why the microphone is configured before anything else starts.** The very first thing ``initialize()`` does is call ``prepare_microphone()``, which runs nine ``amixer cset`` commands against card 0: it switches the capture route through to ``SWR_MIC``, enables the ADC2 input, and — crucially — sets ``ADC2 Volume`` and ``TX_DEC0 Volume``. This is not cosmetic. The board's saved audio state leaves the capture gain at its minimum, and a speech Brick from an earlier app can leave the capture route switched off altogether. In either case the wake-word model runs perfectly, evaluates windows, reports no error at all — and hears nothing, because the audio reaching it is nearly silent. Measured on this kit, normal speech registers an RMS of about 67 with the saved settings and about 1200 with the values above. Because the whole loop is wrapped in ``try``/``except``, a failure here does not crash the app: it prints ``[MIC] Could not configure the microphone: ...`` and carries on with whatever state the board was already in — which is your first clue to look for if the model never hears you.

**The heartbeat — how a console app proves it is alive.** With no Web UI there is no spinner, no status dot, and no error banner: the console is the only window into the board, and while nothing is being recognised it would otherwise stay completely silent. The heartbeat thread therefore prints a line every ``HEARTBEAT_SECONDS`` (15 seconds) — ``[LISTENING] Microphone active. wakes=0, last wake 15s ago.`` while it waits, ``[WAIT] Still starting up...`` during boot, and ``[BUSY] Handling a command. (wakes=N)`` mid-interaction. Those lines are not decoration. A steady ``[LISTENING]`` line with ``wakes=0`` tells you the microphone is capturing and the model is evaluating windows, and that the only thing missing is a match for your voice — which is a completely different problem from a dead app.

**Why there is no Web UI.** Two reasons, one technical and one human. The technical one lives in ``app.yaml``::

   bricks:
   # keyword_spotting MUST stay first: if it is listed after another audio brick
   # it takes over the Web UI port (4912) and the app misbehaves.
   - arduino:keyword_spotting:
       model: keyword-spotting-hey-arduino
   - sunfounder_stt: {}
   - sunfounder_tts: {}

The keyword spotter takes over the port App Lab uses to serve a Web UI, so declaring it after another audio Brick leaves the app fighting over the same socket. The human reason is simpler: nothing here needs a browser. Every event in this project is a line of text — wake, heard, action — and the RGB LED is the display. A Web UI would add a screen to an interaction that is supposed to be hands-free.

3. Experiment
---------------

**Talk to It, and Watch What It Thinks**

The console prints the model's opinion for every window, so you can watch each experiment happen instead of guessing.

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - You do
     - Result
   * - Stand well back — two metres or more — and say "Hey Arduino"
     - Fewer windows clear the 0.45 threshold; you may see ``Keyword 'other'`` or ``Keyword 'background'`` win instead. Step closer and repeat
   * - Start your command before "I'm here." has finished playing
     - Those first words land before ``stt.start_listening()`` runs, so ``[HEARD]`` misses them — the app records four seconds starting *after* the reply, not during it
   * - Say "Turn the light orange."
     - ``[HEARD] turn the light orange.`` followed by ``[ACTION] No supported light command in that sentence.`` — the sentence was transcribed perfectly, but ``orange`` is not a preset
   * - Say "Turn the light blue and red." in one breath
     - The light goes **red**. Presets are checked in a fixed order and the first name found anywhere in the sentence wins, so the order you *said* them in does not matter

**Challenge: Teach It Your Voice**

The wake-word model that ships with the kit was trained on a **single speaker's** voice, so it may simply never recognise how you say "Hey Arduino" — the console will keep printing ``Keyword 'background' detected ...`` while you speak, no matter how loudly or how carefully you try. Before you blame yourself, look at the confidence numbers and try moving ``CONFIDENCE`` up and down: does a lower threshold let you through, and does it also make the assistant wake when nobody spoke? Then take the real fix. App Lab's **AI Model** page (choose **Train new AI Model**) hands your project to Edge Impulse Studio, where you can record your own "Hey Arduino" samples, train a keyword-spotting model on your own pronunciation, deploy it, and point ``app.yaml`` at your model instead of ``keyword-spotting-hey-arduino``. There is no single right answer here — the goal is to find out how much of "the model doesn't work" was really "the model wasn't trained on me".

**Challenge: Make the Command Visible**

You may have noticed that the new colour appears for only an instant: the LED flashes the colour you asked for, then goes dark, because the ``finally`` block in ``handle_command()`` always ends with ``set_light(0, 0, 0)``. That reset exists so the light returns to a clean state between interactions — but it also means the light never *stays* on. Decide what this lamp should do when it is not talking to you, and make it happen: keep the colour until the next command, let it fade back to the dim green standby cue, pulse it while waiting, or something else entirely. The interesting question is not just how to stop the reset, but which behaviour makes the lamp's state readable from across the room.

4. Troubleshooting
--------------------

**It never wakes up, and the console keeps printing ``Keyword 'background' detected``**

* **Cause:** The model is hearing you but classifying the window as room noise rather than as the wake word. Two things cause this: your pronunciation does not match the single speaker the shipped model was trained on, or almost no audio is reaching the model at all.
* **Solution:** First confirm the microphone line appeared at startup: ``[MIC] Capture route and gain applied ...``. If it did not, the capture gain is probably still at its minimum — look for the ``[MIC] Could not configure the microphone`` message and run the app again. Then speak from about 30 cm, in a quiet room, and watch the class and the confidence the model prints: if you only ever see ``background``, try raising or lowering ``CONFIDENCE`` in steps of 0.05, and if the score for ``hey_arduino`` stays low, train your own wake-word model on your own voice — the shipped one was trained on a single speaker, so it may simply never match you.

**The console stays completely empty after you press Run**

* **Cause:** The app never got as far as running its Python code. Usually the keyword-spotting model is not installed, or the Brick list in ``app.yaml`` is wrong, so App Lab stops before ``initialize()`` prints anything.
* **Solution:** Check the app's own error banner in App Lab and stop and Run the app again. When the model is missing you normally see a ``[STARTUP ERROR]`` line rather than silence, so a genuinely blank console points at the app itself — make sure ``app.yaml`` declares all three Bricks with ``arduino:keyword_spotting`` **first**, and remember there is no Web UI tab to open in this project: the Output console is where everything appears.

**It wakes, but the spoken command is not understood**

* **Cause:** The four-second recording window closed before your sentence finished, the room was too noisy for the small local Whisper model, or the sentence had no colour word in it.
* **Solution:** Wait for "I'm here." to finish, then speak immediately — the recording starts as soon as the reply ends and lasts four seconds. Keep commands short and use the preset vocabulary: *"turn the light blue"*, or *"turn the light off"*. Note that *"turn the light on"* with no colour is not a supported command, so it produces the "no supported light command" line. Reading ``[HEARD]`` tells you whether the problem is the recogniser (wrong words) or the matcher (right words, no preset in them).

**It wakes and the console works, but there is no sound**

* **Cause:** On the first run, App Lab is still downloading and preparing the TTS runtime and the EdgeTTS voice data — this can take half an hour or more. A TTS failure is caught by the code, so the rest of the app keeps running without it.
* **Solution:** Keep the UNO Q connected to the Internet and wait for the setup to finish; it only happens once. Once startup prints ``[OK] Text to speech ready.`` you should hear the reply. If you see ``[TTS] failed: ...`` or ``[WARN] Text to speech failed, commands still work`` instead, the light will still respond — check that the Multimedia Carrier is firmly attached.

**The wake word triggers on its own**

* **Cause:** ``CONFIDENCE`` is set to 0.45, lower than the Brick's default of 0.8, so words that merely sound like "Hey Arduino" — or background speech and music — can clear the bar.
* **Solution:** Raise ``CONFIDENCE`` towards 0.6 or higher and say the wake word yourself to see how much confidence you actually score; pick a threshold above the false triggers and below your own typical score. The console's per-window lines are the measurement tool here: they show you the number the model gave each window, so you are tuning against data instead of a guess.

5. Summary
-------------

You just taught your UNO Q to wait for its name and obey your voice — a lamp that turns on when spoken to, with no button, no browser, and no keyboard anywhere in the loop. In this project, you learned:

* How a **two-stage always-listening pipeline** works: a small keyword spotter judges every one-second window, and the heavy recogniser only runs after the wake word clears the threshold
* What that split buys you — privacy (the room is classified, never transcribed), CPU (four seconds of Whisper instead of all day), and responsiveness (an instant wake word)
* Why ``prepare_microphone()`` writes ALSA mixer settings before the models start, and how a silent capture route makes a healthy model look broken
* How one recognised sentence becomes hardware: first-match substring lookup in ``COLOR_PRESETS`` → ``Bridge.call("set_rgb", r, g, b)`` → ``analogWrite()`` on **D8**, **D7**, and **D6**
* Why a console-only app needs a 15-second heartbeat, and how to read the model's per-window confidence to tell "it can't hear me" apart from "it doesn't recognise me"

That was the last Edge AI project in this module — you have given your board eyes, and now a name it answers to. Next, you will go one step further and actually hold a **conversation** with your UNO Q, using large language models that understand full sentences, remember context, and can call your hardware as a tool.
