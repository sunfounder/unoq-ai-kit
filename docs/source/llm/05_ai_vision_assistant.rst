05 AI Vision Assistant
======================

.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

Every conversation in this module so far started with words you typed. This project hands the model something no amount of typing can describe: a picture. Point the camera at a mug, a toy, or your own hand, ask *"What is this?"* or *"How many are there?"*, and the answer comes back on the page — and out loud, from the board's speaker. Nothing in the app ever "sees" the picture; Python captures a frame, ships it to a vision-capable model, and reads back whatever sentence comes home.

In this lesson, you will learn to:

* Capture frames from the Multimedia Carrier camera in Python, flip them upright, and stream them to the browser
* Send an actual image — not just words — to a vision-capable cloud model, and write a system prompt that keeps it honest about what it can see
* Keep the slow work off the main path: the cloud request and the spoken answer run on a worker thread while the live preview keeps moving
* Report each stage of the exchange — capturing, thinking, speaking, ready — to the one browser that asked
* Hear the answer instead of only reading it, using the ``sunfounder_tts`` brick

1. Setup
-----------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * USB-C Cable
     -
     -
   * - |list_pan_tilt|
     - |list_usb_cable|
     -
     -

**Software Requirements**

This project uses three App Lab **Bricks** — support packages that App Lab adds to your app for you:

* ``web_ui`` — serves the camera page and carries messages between the browser and Python
* ``cloud_llm`` — sends your question together with a camera frame to a cloud vision model and returns the answer
* ``sunfounder_tts`` — turns the finished answer into speech on the board's speaker

Because the model is reached over the internet, the project needs a key of your own. ``app.yaml`` declares the ``cloud_llm`` brick with an empty ``API_KEY``, so App Lab asks you for an **OpenAI API key** the first time you press **Run** and stores it for you.

There are no sketch libraries to install: this project has no ``sketch/`` folder at all, so nothing is compiled for the MCU and nothing crosses the Bridge.

**Hardware Check**

#. The kit arrives assembled — the UNO Q sits on the Robot Shield and the Multimedia Carrier is pressed onto the connectors. Check that the carrier is fully seated, because the camera and the speaker both live on it.
#. Look at the camera at the front of the carrier. Its ribbon cable must be clicked firmly into its connector with the **blue side facing up**, and the lens must be clear of the bracket that holds it.
#. Make sure the carrier's **speaker** is not covered or resting on the desk — the answer is read aloud as well as printed.
#. Plug the **USB-C cable** into the UNO Q and your computer, and check that the board powers up.

No breadboard wiring is needed in this lesson: the camera, the speaker, and the whole "circuit" are already built into the Multimedia Carrier.

.. note::

   Before using the camera, make sure external carriers are enabled on your UNO Q — this is a one-time setup: :ref:`enable_external_carriers`. A camera is never hot-swappable: disconnect the battery and the USB-C cable before you plug one in.

2. Run the App
----------------

#. Download :download:`05 AI Vision Assistant.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/05.AI.Vision.Assistant.zip>`.
#. Open **Arduino App Lab** and go to **Apps**. Click the dropdown arrow next to **Create new app +** and select **Import App**.

   .. image:: /img/app_import_app.png
      :width: 600

#. Select **Import from Computer**.

   .. image:: /img/app_import_pc.png
      :width: 600

#. Choose the package you downloaded. The app appears in **Apps** — click it to open.
#. With the app open, click the **Run** button (▶) in the top-right corner. Python opens the camera and starts capturing frames — there is no sketch in this project, so nothing is flashed to the board.

   .. image:: /img/app_run.png
      :width: 500
      :align: center

   .. note::

      The first time you run this project, App Lab asks for your **OpenAI API key**, because the app uses the ``cloud_llm`` brick to reach the model. Paste a key from your OpenAI account and save it — App Lab keeps the key for your board, so you only do this once.

#. The Output window prints *"AI Vision Assistant ready."* and a **Web UI** tab opens by itself. The status row reads **Connecting** for a moment, then **Connected** with a blue dot, and the live camera view appears inside the frame.
#. Point the camera at something — a mug, a toy, your hand — and type a question in the box. The default text is *"What can you see?"*, and you can ask anything the picture could answer: *"What colour is it?"*, *"What is on the left?"*, *"How many fingers am I holding up?"*. Then click **ASK AI**.
#. The status panel walks through its stages while the answer is on its way: **Image Captured**, then **Thinking** with *"AI is looking at the image..."*, then **Speaking...** as the reply is read aloud. The button reads **PLEASE WAIT** and the box is locked for as long as this takes.
#. The answer lands in the **AI answer** card and the panel returns to **Ready**. The page looks like this — the live view at the top, the assistant's current state below it, and the question box underneath.

   .. image:: img/ai_vision_assistant.png
      :width: 600
      :align: center

**How it Works**

Here is the whole path a question travels — into the camera, up to the cloud, and back to you as a sentence you can hear.

An App Lab project is a folder of files. Here is what is inside this one:

* ``05 AI Vision Assistant/`` — the app folder

  * ``app.yaml`` — app metadata: name, icon, and the three Bricks the project declares
  * ``README.md`` — a short guide to the project

  * ``python/``

    * ``main.py`` — the camera loop, the MJPEG stream, the vision request, and the spoken answer

  * ``bricks/``

    * ``sunfounder_tts/`` — the text-to-speech brick the app ships with: the local voice server behind ``tts.say()``

  * ``assets/``

    * ``index.html`` — the assistant page: status row, camera frame, state panel, question box, and answer card
    * ``app.js`` — browser logic: the socket events, the state panel, and the stream retry
    * ``style.css`` — the visual styling of the page
    * ``libs/socket.io.min.js`` — the Socket.IO client that carries messages between the page and the board
    * ``img/sf_logo.png`` — the logo in the page header
    * ``docs_assets/`` — the result image used by this documentation

There is no ``sketch/`` folder here — nothing is flashed to the MCU, the Bridge is never used, and the entire app is Python running on the Linux MPU.

The data path, from a camera frame to a spoken answer:

.. mermaid::

   sequenceDiagram
       participant B as Browser (HTML/JS)
       participant P as Python (main.py)
       participant C as Camera (carrier CSI)
       participant L as Vision LLM (gpt-4o-mini)
       participant S as Speaker (sunfounder_tts)

       C->>P: camera.capture() - one frame, 20 per second
       P->>P: cv2.flip(frame, 0) - upright
       P->>P: cv2.imencode(".jpg", frame, 85) - JPEG bytes into current_frame
       B->>P: GET /stream - the MJPEG preview
       P-->>B: multipart/x-mixed-replace frames
       B->>P: socket.emit("ask_ai", {question})
       P->>P: copy the newest frame, start a worker thread
       P->>L: vlm.chat(message=question, images=[frame])
       L-->>P: a one- or two-sentence answer
       P-->>B: socket "vision_status" - the answer
       P->>S: tts.say(answer)
       P-->>B: socket "vision_status" - ready

Here is what each piece does:

**Python (main.py)** — runs on the Linux MPU
  * ``Camera(fps=20)`` is the whole camera setup — an App Lab peripheral, not a brick
  * ``loop()`` runs over and over: ``camera.capture()`` takes a frame, ``cv2.flip(frame, 0)`` turns it the right way up, and ``cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])`` compresses it into JPEG bytes that are parked in a shared ``current_frame`` under ``frame_lock``
  * ``with camera: App.run(user_loop=loop)`` opens the camera before the first frame and runs that loop for as long as the app lives
  * ``ui.expose_api("GET", "/stream", video_stream)`` adds one extra route to the Web UI server; ``video_stream()`` answers it with a ``StreamingResponse`` of ``multipart/x-mixed-replace`` frames, which is what makes the picture move in the browser
  * ``ui.on_message("ask_ai", ask_ai)`` listens for the question the page sends
  * ``ask_ai()`` refuses an empty question, trims it to 300 characters, declines a second question while ``busy`` is set, copies the newest frame, and hands the real work to ``threading.Thread(target=process_question, ...)`` so the preview never stutters
  * ``CloudLLM(model="openai:gpt-4o-mini", system_prompt=SYSTEM_PROMPT, temperature=0.3, max_tokens=160)`` creates the link to the vision model and fixes its behaviour up front
  * ``vlm.chat(message=question, images=[frame])`` is the key call — the question and the JPEG frame travel together, and an empty answer is replaced with *"Sorry, I could not describe the image. Please try again."*
  * ``vlm.with_memory(max_messages=0)`` stops old images from piling up in the conversation, so each question is answered from the current frame only
  * ``tts.say(answer)`` speaks the reply, and ``ui.send_message("vision_status", {...}, room=sid)`` reports every stage of the exchange back to the single browser that asked

**Camera (App Lab peripheral)** — the Multimedia Carrier's CSI camera
  * ``camera.capture()`` returns the newest frame, and the camera keeps producing them at 20 per second whether or not anybody is looking
  * The camera sits upside down in the carrier's bracket, so the vertical flip is what makes both the preview and the picture the model receives upright — the two always agree, because both come from that one ``current_frame``
  * No brick is involved: the camera comes with App Lab itself, which is why the whole setup is one line

**Vision LLM (behind the ``cloud_llm`` brick)** — runs on OpenAI's servers
  * The **system prompt** makes it a friendly visual assistant for students: answer only from what is visible in the supplied image, say so clearly when the picture cannot answer the question, keep it to one or two sentences, and reply in the language the question was asked in
  * ``temperature=0.3`` keeps the wording steady and ``max_tokens=160`` keeps the answer short — which also keeps the spoken version short
  * This is the only step that needs the internet, and the only step that costs money

**Text-to-Speech (behind the ``sunfounder_tts`` brick)** — runs on the board
  * ``EdgeTTS()`` with ``set_voice("en-US-JennyNeural")`` and ``set_volume(50)`` prepares the voice
  * ``tts.say(answer)`` speaks the finished sentence while the page shows **Speaking...**
  * The voice reads the answer *after* the model has answered, so audio and text always say the same thing

**Browser (HTML/JS)** — runs in your browser
  * ``socket.emit('ask_ai', {question})`` sends what you typed; the question form's submit handler is the only place that happens
  * ``cameraStream.src = http://<host>:7000/stream?r=<timestamp>`` loads the MJPEG stream into an ``<img>``, and the ``error`` listener retries it every 1.5 seconds if the picture drops
  * ``socket.on('vision_status', updateState)`` repaints the state panel from the ``state``, ``message``, and ``answer`` fields, and swaps the button between **ASK AI** and **PLEASE WAIT**
  * ``stateTitles`` gives each state its label — Ready, Image Captured, Thinking, Speaking, Error
  * ``socket.on('connect')`` starts the stream, while ``socket.on('disconnect')`` clears the picture and turns the status dot red

Notice that Python never understands the picture. It does not look for a mug or count fingers — it captures bytes, hands them to a model, and speaks the sentence that comes back. Everything that keeps the exchange orderly is written in ordinary code: one frame in memory, one question at a time, a 300-character limit, and a preview that keeps running on its own thread. The model supplies the understanding; the code supplies the discipline.

3. Experiment
----------------

**Point It at the World and Ask**

The model answers only from the picture it was handed, so what you show it *is* the experiment. Try each of these and compare the card on screen with what you hear:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - What you show the camera
     - What you ask — and what comes back
   * - A mug, a bottle, or a toy on the desk
     - *"What is this?"* — the model names the object and describes how it looks in a sentence or two
   * - Two or three objects side by side
     - *"Which object is on the left?"* — the answer depends on where things sit inside the frame, which is something only an image can tell it
   * - Your hand with some fingers raised
     - *"How many fingers am I holding up?"* — a counting question the picture answers at once
   * - An empty desk or a blank wall
     - *"What is on the desk?"* — the system prompt tells it to admit when the image cannot answer, so the reply should say that nothing is visible rather than invent an object
   * - Anything at all, asked in another language — *"¿Qué ves?"*
     - The system prompt asks for an answer in the language of the question, so the reply comes back in Spanish and the voice reads that same sentence aloud

**Challenge: Ask Questions the Picture Cannot Answer**

The prompt promises the assistant will only answer from the image, and that it will say so when the picture cannot answer. Test that promise. Ask about things that are not in the frame at all — *"What is my name?"*, *"What did I do yesterday?"*, *"Is it raining outside?"*. Then ask about something that *is* there but is genuinely hard to see: the colour of a dark object in shadow, the brand name on a pen, how many pages are left in a closed book. Keep a tally of how often the assistant admits it does not know and how often it answers anyway. There is no correct total to reach — the point is to see where a model that has been told to stay honest still feels free to guess, and to notice that a confident answer is not the same thing as a correct one.

**Challenge: Make the Picture Harder to Read**

Same object, changing conditions. Show it in dim light, then with a bright window behind it, then very close, then far away, then tilted, then half hidden behind your hand. Note which conditions still get an accurate answer and which produce something confident but wrong. Then watch what the *frame* means: the question is answered from the single frame that was in memory the moment you clicked, so if you move the object right after clicking, the page will show the new position while the model is still describing the old one. How much can you change the scene before the answer stops matching what you see?

4. Troubleshooting
--------------------

**The camera frame stays dark and reads "Waiting for camera..."**

* **Cause:** No frames are arriving at all. The usual reasons are that external carriers were never enabled, that the camera type for the connector the camera uses was not selected, or that the ribbon cable is not fully seated.
* **Solution:** Complete the one-time setup at :ref:`enable_external_carriers`, choosing the type that matches the connector your camera is plugged into, then let the board reboot. Reseat the ribbon cable with the blue side up and both ends clicked in, and run the app again. The page retries the stream by itself every 1.5 seconds, so you rarely need to reload it.

**The status panel says "The camera image is not ready yet. Please try again."**

* **Cause:** You clicked **ASK AI** before the first frame had been captured, so the shared ``current_frame`` was still empty and there was nothing to send to the model.
* **Solution:** Wait until the live view is moving before you ask. If the preview never starts, fix that first — this message is only about the picture not being there yet, not about the question or the API key.

**The status panel turns red with "Vision assistant error: ..."**

* **Cause:** The request to the vision model failed. Every failure ends up here: no key saved yet, a key that was rejected or has run out of credit, or no internet connection on the board. The code prints the exception type, which is the fastest clue to which of the three it was.
* **Solution:** Check the board's internet connection first, since the model lives in the cloud. Then confirm your key is still valid and funded in your OpenAI account, stop the app, and press **Run** again to enter a fresh key. A red panel *and* total silence from the speaker almost always means the cloud request never came back at all.

**The answer takes a long time to arrive**

* **Cause:** The whole JPEG frame plus your question travel to OpenAI's servers, and the finished answer comes back in one piece — there is no streaming to watch here. The code also allows only one question at a time, so a second click while the first is still working is answered with *"Please wait for the current answer."*
* **Solution:** Watch the state panel rather than the button: **Thinking** means the model is working, **Speaking...** means the board is talking. The first question after **Run** is the slowest, because the connection to the model is still being established. Short, specific questions return fastest, and the 160-token limit exists to keep answers brief enough to listen to.

**The answer does not match what you are pointing at**

* **Cause:** Only one frame is sent — the one in memory at the instant you clicked. Move the camera or the object afterwards and the answer still describes the earlier view. Dim light, a cluttered desk, or a small object in a large frame can also lead the model to describe something other than what you had in mind.
* **Solution:** Fill the frame with one object, hold it still for a moment, and then click **ASK AI**. Ask a question that names what you want to know (*"What colour is the mug?"*) instead of an open one, and improve the lighting before you blame the model.

5. Summary
-------------

You just taught your UNO Q to look. The board takes a picture, sends it into the cloud with a question attached, gets a short answer back, and reads that answer to you out loud.

* A picture is just data: ``camera.capture()`` hands Python a frame, and ``cv2.imencode()`` shrinks it into JPEG bytes small enough to send
* The vision model is reached exactly like every other model in this module — one ``CloudLLM`` object, one ``chat()`` call — except that the message now travels with ``images=[frame]``
* The **system prompt** is what keeps a vision model honest: answer only from the image, admit when the picture cannot answer, stay brief, and reply in the reader's language
* The slow half of the work runs on a worker thread, so the live preview never freezes, and a ``busy`` flag keeps exactly one question in flight
* ``ui.send_message(..., room=sid)`` shows how a Web UI can answer one browser instead of all of them — every state change goes back only to the person who asked

This is the last project in this module, and it is worth looking back at how far one idea has travelled. First the model chose a colour from a list, then it held a conversation and picked a mood at the same time, and now it looks at the world and tells you what it sees. The board did not change — the camera, the speaker, and the Web UI were always there. What changed was the question you sent and the rules you wrapped around the answer. That is the whole skill this module has been building: the model supplies the understanding, and your code decides what is allowed to happen next. You have used it to light an LED, to pull a face, and now to see — and every project you build from here can reuse the same three pieces: an input on the board, a model for judgement, and a page that shows you what happened.
