04 AI Voice Assistant
======================

.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

Every project so far has taken its orders from a keyboard: a sentence typed into a box, a slider dragged with a mouse. This project takes the keyboard away. You hold a button on the page, **say a question out loud**, and the UNO Q writes your words down on the board itself, sends only those words to a cloud language model, and answers you in a voice of its own. Three different AI services cooperate in a single loop — and you never type a character.

In this lesson, you will learn to:

* Chain three AI services into one loop: **speech recognition**, a **cloud language model**, and **text to speech**
* Use **hold-to-talk** recording — audio is captured only between a button press and a release, and the page stays responsive while the answer is prepared
* Run speech recognition **on the board** — the Whisper model travels inside the package, so your voice never has to leave the UNO Q
* Give the model a **system prompt** that decides how the assistant answers, and hear that decision in every reply
* Follow one spoken sentence through the status panel: Listening, Recognizing, Thinking, Speaking, Ready

1. Setup
-----------

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

**Software Requirements**

This project uses four App Lab **Bricks** — support packages that App Lab adds to your app for you:

* ``web_ui`` — serves the hold-to-speak page and keeps the browser and Python in sync
* ``cloud_llm`` — sends the recognized sentence to a cloud language model and streams the answer back
* ``sunfounder_stt`` — speech recognition that runs **on the board**, with the Whisper model that ships inside the package
* ``sunfounder_tts`` — turns the answer text into speech and plays it through the carrier's speaker

There is no sketch in this project and no sketch libraries to install: nothing here drives a pin, so every line of it runs in Python on the Linux MPU.

Because the model is reached over the internet, the project needs a key of your own. ``app.yaml`` declares the ``cloud_llm`` brick with an empty ``API_KEY``, so App Lab asks you for an **OpenAI API key** the first time you press **Run** and stores it for you. The two speech Bricks need no key at all — and because both of them travel inside the package, together with the Whisper model, this download is much larger than the other projects in the module.

**Hardware Check**

#. Check that the **Multimedia Carrier** is sitting firmly on the UNO Q — the microphone and the speaker this project uses are built into it.
#. Plug the **USB-C cable** into the UNO Q and your computer, and check that the board powers up.
#. Stand the board on the table in front of you with the carrier's microphone facing you, about 30–50 cm away, and keep the room reasonably quiet for your first attempt.

No breadboard wiring is needed here: the ears and the voice belong to the Multimedia Carrier, so the kit works exactly as it comes out of the box.

.. note::

   The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

2. Run the App
----------------

#. Download :download:`04 AI Voice Assistant.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/04.AI.Voice.Assistant.zip>`.
#. Open **Arduino App Lab** and go to **Apps**. Click the dropdown arrow next to **Create new app +** and select **Import App**.

   .. image:: /img/app_import_app.png
      :width: 600

#. Select **Import from Computer**.

   .. image:: /img/app_import_pc.png
      :width: 600

#. Choose the package you downloaded. The app appears in **Apps** — click it to open.
#. With the app open, click the **Run** button (▶) in the top-right corner. The Output window prints *"AI Voice Assistant ready."*

   .. image:: /img/app_run.png
      :width: 500
      :align: center

   .. note::

      The first time you run this project, App Lab asks for your **OpenAI API key**, because the app uses the ``cloud_llm`` brick to reach the model. Paste a key from your OpenAI account and save it — App Lab keeps the key for your board, so you only do this once.

#. A **Web UI** tab opens by itself. The status row reads **Connected** with a blue dot, the panel shows **Ready** with the line *"Hold the button and speak."*, and the big button reads **Hold to Speak**.
#. Press and hold the button. The panel turns amber and switches to **Listening...**, and the button label changes to **Release to Finish**.
#. Still holding, say a short question out loud — *"What is the capital of France?"* — then let go. The label becomes **Please Wait**, the button greys out, and the panel walks through **Recognizing your speech...**, **AI is thinking...**, and **Speaking...** before returning to **Ready**.
#. Your sentence appears in the **You said** card, the model's answer appears in the **AI reply** card, and the carrier's speaker reads the answer out loud. Ask a few more questions the same way — hold, speak, release — and each one gets its own answer.
#. The page looks like this while the conversation is running, with the status panel above the button and the two cards underneath.

   .. image:: img/ai_voice_assistant.png
      :width: 600
      :align: center

**How it Works**

The whole project is one loop with three services in the middle: your voice goes in at one end, and the answer comes back out of the speaker at the other.

An App Lab project is a folder of files. Here is what is inside this one:

* ``04 AI Voice Assistant/`` — the app folder

  * ``app.yaml`` — app metadata: name, icon, and the four Bricks the project declares
  * ``README.md`` — a short guide to the project

  * ``python/``

    * ``main.py`` — the hold-to-talk handlers, the recognition → model → speech pipeline, and the status messages

  * ``assets/``

    * ``index.html`` — the page: status row, status panel, the hold-to-speak button, and the two transcript cards
    * ``app.js`` — browser logic: the press-and-hold button, the state panel, and the heard and reply text
    * ``style.css`` — the visual styling of the page
    * ``libs/socket.io.min.js`` — the Socket.IO client that carries messages between the page and the board
    * ``img/sf_logo.png`` — the logo in the page header
    * ``docs_assets/`` — the result image used by this documentation

  * ``bricks/`` — the two speech Bricks travel inside the package, together with the Whisper model they run on

There is no ``sketch/`` folder in this app: nothing here has to reach the microcontroller, so the whole project runs in Python. The data path, from a pressed button to a spoken answer:

.. mermaid::

   sequenceDiagram
       participant B as Browser (HTML/JS)
       participant P as Python (main.py)
       participant S as Speech Recognition (sunfounder_stt)
       participant L as Cloud LLM (OpenAI)
       participant V as Text to Speech (sunfounder_tts)

       B->>P: socket.emit("start_recording")
       P->>S: stt.reset() + stt.start_listening()
       P-->>B: ui.send_message("voice_status", "listening")
       B->>P: socket.emit("stop_recording")
       P->>S: stt.stop_listening()
       S-->>P: stt.get_result(timeout=60) - "what is the capital of france"
       P->>L: llm.chat_stream(message=heard)
       L-->>P: the answer, a few words at a time
       P->>V: tts.say(reply)
       V-->>P: audio through the carrier's speaker
       P-->>B: ui.send_message("voice_status", {state, message, heard, reply})
       B->>B: updateState() - panel, button label, both cards

Here is what each piece does:

**Python (main.py)** — runs on the Linux MPU
  * ``WebUI()`` starts the server that hands the page in ``assets/`` to your browser
  * ``ui.on_message("start_recording", start_recording)`` and ``ui.on_message("stop_recording", stop_recording)`` listen for the two button events
  * ``STT(type="local_fast", language="en")`` creates the local recognizer, and ``stt.reset()``, ``stt.start_listening()``, ``stt.stop_listening()`` and ``stt.get_result(timeout=60)`` are the four calls that capture and transcribe one sentence
  * ``stt.get_result()`` may come back empty — an empty answer stops the loop there and tells the page nothing was recognized
  * ``CloudLLM(model="openai:gpt-4o-mini", system_prompt=SYSTEM_PROMPT)`` creates the link to the cloud model and fixes its behaviour up front
  * ``llm.chat_stream(message=heard)`` sends the recognized sentence and streams the answer back in pieces, which are joined into one reply
  * ``EdgeTTS()``, ``tts.set_voice("en-US-JennyNeural")``, ``tts.set_volume(50)`` and ``tts.say(reply)`` choose a voice and speak the answer
  * ``ui.send_message("voice_status", {...})`` keeps the page informed of the state, what was heard, and what was answered
  * ``threading.Thread(target=process_voice, daemon=True)`` keeps the button handler free while recognition, the model, and the voice do their work
  * ``os.makedirs("/app/audio_output", exist_ok=True)`` creates the folder where the speech Bricks drop their temporary audio files
  * ``App.run()`` starts the app and keeps it alive

**Speech Recognition (behind the ``sunfounder_stt`` brick)** — runs in its own service on the board
  * ``stt.start_listening()`` opens the carrier's microphone and records until you release the button
  * ``stt.stop_listening()`` closes the recording and hands the audio to the **Whisper** model
  * ``stt.get_result(timeout=60)`` returns the text — the words that end up in the **You said** card
  * The model is a small Whisper build that ships inside the package, so this step needs no key and no internet: your voice is transcribed on the UNO Q itself

**Cloud LLM (behind the ``cloud_llm`` brick)** — runs on OpenAI's servers
  * The **system prompt** introduces a *friendly voice assistant* and asks for a natural answer of one or two sentences, in whatever language you used
  * Your sentence is sent with that instruction over the internet, and the answer streams back as text
  * This is the only step that asks for your **API key** — the reasoning happens in the cloud

**Text to Speech (behind the ``sunfounder_tts`` brick)** — the brick runs on the board and the voice is synthesized online
  * ``tts.say(reply)`` turns the answer text into audio and plays it through the Multimedia Carrier's speaker
  * The voice is fixed to ``en-US-JennyNeural`` at volume 50 in ``main.py``; the voice service needs an internet connection, but never a key
  * The first run downloads the runtime this Brick needs, which is why the very first conversation takes so long to speak

**Browser (HTML/JS)** — runs in your browser
  * ``socket.emit('start_recording', {})`` fires on ``pointerdown`` and ``socket.emit('stop_recording', {})`` on ``pointerup``, so the button really is a push-to-talk switch
  * ``socket.on('voice_status', updateState)`` repaints the panel, the button label, and both transcript cards
  * The ``stateTitles`` map names the six states the panel can show — Ready, Listening, Recognizing, Thinking, Speaking, and Error
  * While the app is busy the button is disabled and reads **Please Wait**, and ``window.addEventListener('blur', ...)`` releases it for you if you click away mid-sentence
  * ``socket.on('connect')`` and ``socket.on('disconnect')`` drive the status dot, and an error state fills the red banner with the message Python sent

Notice how the loop is split: the listening half never leaves the board, the thinking half happens in the cloud, and the speaking half comes home again. What travels over the internet is only text — the sentence the recognizer wrote down and the answer the model wrote back. The model never touches the hardware either: this project has no Bridge call and no sketch, so words are the only thing it can produce.

3. Experiment
----------------

**Ask It Anything**

Speak each request in your normal voice and watch the panel, the two cards, and the speaker at the same time:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - What you say
     - What happens
   * - *"What is the tallest mountain in the world?"*
     - Your sentence lands in **You said**, the panel runs through Recognizing → Thinking → Speaking, the answer appears in **AI reply**, and the speaker reads it out
   * - *"Tell me a joke."*
     - The answer stays short — one or two sentences, as the assistant's instructions ask — instead of turning into a long routine
   * - *"¿Cuál es la capital de Francia?"*
     - The answer text comes back in Spanish, because the assistant was told to reply in the language you used; it is still read aloud in the one English voice the project selected
   * - *"Turn the light red."*
     - Nothing in the room changes. There is no sketch and no hardware call in this project, so words are all the assistant can produce — and some replies will cheerfully claim the light is red, which is exactly the illusion words alone can create
   * - Releasing the button without speaking
     - The panel returns to **Ready** with *"No speech was recognized. Hold the button and try again."* — an empty recording is dropped before it ever reaches the model

**Challenge: Find the Edges of "Briefly"**

The assistant is told to answer in one or two sentences, so put that instruction under pressure. Ask for the longest answer you can get — *"Explain how rainbows form, in detail."*, *"Tell me the entire history of the UNO Q."* — then ask it to be verbose, then ask a question that can be answered with a single word. Compare the lengths in the **AI reply** card each time. Which wins more often: your wording, or the instruction the code gave the model?

**Challenge: Hear What the Recognizer Heard**

The card under **You said** is not what you said — it is what the recognizer heard, and the two do not always agree. Try to pull them apart: speak from across the room, whisper, talk very fast, switch on a fan or some music, or slip into another language or a made-up word. Every time the text differs from your intention, you are looking at the weakest link in the chain. Then watch what the assistant does with the misheard sentence — it will answer the question it was handed, not the one you meant, because text is the only thing it ever receives.

4. Troubleshooting
--------------------

**The red banner reports "Voice assistant error: ..."**

* **Cause:** The request to the cloud model failed. The app shows this message for any failure at all: no key saved yet, a key that was rejected or has run out of credit, or no internet connection on the board.
* **Solution:** Check the board's internet connection first, since the model lives in the cloud. Then confirm your key is still valid and funded in your OpenAI account, stop the app, and press **Run** again to enter a fresh key.

**The panel says "No speech was recognized..."**

* **Cause:** The recording was silent or too quiet to transcribe. The recognizer found no words in it — usually because the button was released before you started speaking, or because you were too far from the microphone.
* **Solution:** Hold the button first and wait until the panel says **Listening...**, then speak at a normal volume from 30–50 cm away before releasing. If the panel instead shows *"Unable to start recording"*, the microphone itself could not be opened: check that the Multimedia Carrier is firmly attached and that no other app is holding the audio device.

**The answer appears on screen, but you hear nothing**

* **Cause:** The **AI reply** card is filled before the speech starts, so text without sound means recognition and the model both worked and only the voice failed. The usual reasons are a board that has lost its internet connection — the voice is synthesized online — a muted or covered speaker, or something plugged into the headphone jack.
* **Solution:** Check the board's connection first, then the audio: unplug anything in the headphone jack, make sure the carrier's speaker is not covered, and remember the project sets the volume to 50, so a noisy room can swallow it. If the Console shows a speech error, re-run the app once the first-run setup has finished.

**The first run takes half an hour or more**

* **Cause:** Nothing is broken. The first run has real work to do — App Lab downloads and prepares the text to speech runtime and its audio dependencies, and the speech Bricks arrive with the package together with the Whisper model.
* **Solution:** Keep the UNO Q connected to the Internet and let the setup finish. This happens once: after it completes, every speech example starts much faster.

**The Web UI never opens, or the status dot turns red and reads "Disconnected"**

* **Cause:** The app is not running yet, your browser blocked the new tab, or the socket between the page and Python dropped because the app stopped or the board was unplugged.
* **Solution:** Press **Run** again and wait for the *"AI Voice Assistant ready."* line in the Output window, then allow pop-ups for App Lab or open the Web UI from the app's tab strip yourself. If the page lost the board while you were talking, reconnect the USB-C cable if it came loose and refresh the tab — the page reconnects on its own once the app is back.

5. Summary
-------------

You just held a conversation with your UNO Q. It listened through the carrier's microphone, wrote your words down on the board itself, sent only those words to a cloud model, and answered you out loud in a voice it fetched for the occasion — no keyboard, no wiring, just speech in and speech out.

* Three services, one loop: recognition on the board, reasoning in the cloud, and speech on the way back
* Speech recognition stays local — the Whisper model travels inside the package, so your voice never leaves the UNO Q and needs neither a key nor a connection
* A **system prompt** sets the personality and the length of every answer, which is why the assistant stays brief no matter how you phrase the question
* The **You said** card is the honest record of the loop — read it whenever the answer does not match the question you thought you asked
* The status panel is the whole program in five words: Listening, Recognizing, Thinking, Speaking, Ready

Next, the UNO Q gets eyes as well as ears: point a camera at something, ask a question about what it sees, and the answer comes back in the same voice you just built.
