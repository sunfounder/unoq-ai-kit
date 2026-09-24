06 AI Scavenger Hunt
======================

.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

Every project in this module so far gave the model one job. Here it gets two, and they pull in opposite directions. First the model *invents* a challenge — *"Find something red"* — and then, when you hold an object up to the camera, the same model *judges* whether you found it. The mission is spoken aloud, the verdict comes back as a strict piece of JSON, and the board answers with colour and sound: yellow while a mission is live, green with two rising tones when you get it right, red with one low note when you do not.

In this lesson, you will learn to:

* Call a cloud model twice for two very different jobs — one prompt that writes the game, another that referees it
* Ask a vision model for **structured output** and parse it as JSON, so the verdict is a value your code can trust instead of a sentence it has to interpret
* Turn a game event into hardware feedback through one small integer, a ``switch``, an ``analogWrite()``, and a ``tone()``
* Keep the mission, the score, and the attempts in one shared state object, so every screen update is built from the same truth
* Read the difference between a model that is *creative* (``temperature=0.9``) and one that is *careful* (``temperature=0.1``)

1. Setup
-----------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_rgb_led` (common cathode)
     - 3 * :ref:`cpn_resistor` (220Ω)
     - 1 * :ref:`cpn_buzzer`
   * - |list_pan_tilt|
     - |list_rgb_led|
     - |list_220ohm|
     - |list_active_buzzer|
   * - 1 * :ref:`cpn_breadboard`
     - Several :ref:`cpn_wires`
     - 1 * USB-C Cable
     -
   * - |list_breadboard|
     - |list_wire|
     - |list_usb_cable|
     -

**Software Requirements**

This project uses three App Lab **Bricks** — support packages that App Lab adds to your app for you:

* ``web_ui`` — serves the game page and carries the game state between the browser and Python
* ``cloud_llm`` — writes each mission and referees the camera image with a cloud vision model
* ``sunfounder_tts`` — reads the mission and the referee's verdict aloud on the board's speaker

Because the model is reached over the internet, the project needs a key of your own. ``app.yaml`` declares the ``cloud_llm`` brick with an empty ``API_KEY``, so App Lab asks you for an **OpenAI API key** the first time you press **Run** and stores it for you.

There are no libraries to install on the sketch side either: ``sketch.yaml`` declares no ``libraries:`` section at all, so the only code the MCU runs is the sketch itself.

**Wiring Diagram**

The RGB LED has four legs: the longest one is the **common cathode** and goes to **GND**, while the red, green, and blue anodes go to **D8**, **D7**, and **D6**, each through its own **220Ω** resistor. The buzzer sits beside it, with its **+** leg on **D5** and its **−** leg on **GND**. Never connect an LED channel straight to a pin without its resistor — the LED can burn out.

.. image:: /img/wiring/wiring_pc_buzzer_rgb.png
   :width: 600
   :align: center

.. note::

   The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

2. Run the App
----------------

#. Download :download:`06 AI Scavenger Hunt.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/06.AI.Scavenger.Hunt.zip>`.
#. Open **Arduino App Lab** and go to **Apps**. Click the dropdown arrow next to **Create new app +** and select **Import App**.

   .. image:: /img/app_import_app.png
      :width: 600

#. Select **Import from Computer**.

   .. image:: /img/app_import_pc.png
      :width: 600

#. Choose the package you downloaded. The app appears in **Apps** — click it to open.
#. With the app open, click the **Run** button (▶) in the top-right corner. The sketch takes control of the RGB LED and the buzzer, and the Python side opens the camera and starts the Web UI.

   .. image:: /img/app_run.png
      :width: 500
      :align: center

   .. note::

      The first time you run this project, App Lab asks for your **OpenAI API key**, because the app uses the ``cloud_llm`` brick to reach the model. Paste a key from your OpenAI account and save it — App Lab keeps the key for your board, so you only do this once.

#. The Output window prints *"AI Scavenger Hunt ready."* and a **Web UI** tab opens by itself. The status row reads **Connecting** for a moment, then **Connected** with a blue dot, and the live camera view appears inside the frame. Every button stays greyed out until that dot turns blue.
#. Click **NEW MISSION**. The status panel reads **Creating Mission**, the mission card fills with a sentence the model has just invented — something like *"Find something used for writing"* — and the RGB LED turns **yellow**. Once the mission has been spoken, the panel returns to **Ready** and **CHECK OBJECT** becomes available.
#. Show a matching object to the camera and click **CHECK OBJECT**. The panel walks through its stages — **Image Captured**, then **AI Referee Is Thinking**, then **Speaking** — while the referee's one-sentence explanation appears in the **AI Referee** card at the bottom.
#. A match turns the LED **green**, plays two rising tones, adds one point to **Score**, and the status reads **Mission Complete**. A mismatch turns the LED **red**, plays one low note, adds one to **Attempts**, and lets you try the same mission again with another object.
#. Click **RESET** whenever you want a fresh start: the score and attempts go back to zero, the mission is cleared, and the LED goes out.
#. The page looks like this — the score board at the top, the mission below it, the live view in the middle, and the referee's verdict at the bottom.

   .. image:: img/ai_scavenger_hunt.png
      :width: 600
      :align: center

**How it Works**

Here is the whole path a mission travels — written in the cloud, shown to the camera, and answered with light and sound.

An App Lab project is a folder of files. Here is what is inside this one:

* ``06 AI Scavenger Hunt/`` — the app folder

  * ``app.yaml`` — app metadata: name, icon, and the three Bricks the project declares
  * ``README.md`` — a short guide to the project

  * ``python/``

    * ``main.py`` — the mission writer, the camera loop, the referee call, and the Bridge feedback

  * ``sketch/``

    * ``sketch.ino`` — the RGB LED pins, the buzzer notes, and the Bridge function
    * ``sketch.yaml`` — sketch configuration for the UNO Q board

  * ``bricks/``

    * ``sunfounder_tts/`` — the text-to-speech brick the app ships with: the local voice server behind ``tts.say()``

  * ``assets/``

    * ``index.html`` — the game page: score board, mission card, camera frame, status panel, and referee card
    * ``app.js`` — browser logic: the three buttons, the game state, and the stream retry
    * ``style.css`` — the visual styling of the page
    * ``libs/socket.io.min.js`` — the Socket.IO client that carries messages between the page and the board
    * ``img/sf_logo.png`` — the logo in the page header
    * ``docs_assets/`` — the result and wiring images used by this documentation

The data path, from a written mission to a judged object:

.. mermaid::

   sequenceDiagram
       participant B as Browser (HTML/JS)
       participant P as Python (main.py)
       participant C as Camera (App Lab)
       participant L as Cloud LLM (gpt-4o-mini)
       participant S as Sketch (sketch.ino)
       participant T as TTS (sunfounder_tts)

       B->>P: socket.emit("new_mission")
       P->>L: task_llm.chat(message) - write one mission
       L-->>P: "Find something used for writing"
       P->>S: Bridge.call("game_feedback", 1)
       S->>S: setRgb(255, 160, 0) - yellow
       P->>T: tts.say("Your mission is: ...")
       P-->>B: game_state - speaking, then ready
       C->>P: camera.capture() - a frame, 20 per second
       P->>P: cv2.flip(frame, 0), then JPEG bytes
       B->>P: GET /stream - the live preview
       P-->>B: multipart/x-mixed-replace frames
       B->>P: socket.emit("check_object")
       P->>L: judge_llm.chat(message, images=[frame])
       L-->>P: JSON with success true or false
       P->>S: Bridge.call("game_feedback", 2 or 3)
       S->>S: setRgb(0, 255, 0), then two rising tones
       P->>T: tts.say("Mission complete! ...")
       P-->>B: game_state - complete, score plus one

Here is what each piece does:

**Sketch (sketch.ino)** — runs on the STM32 MCU
  * ``setup()`` sets **D8**, **D7**, **D6**, and **D5** to outputs, clears the LED, then calls ``Bridge.begin()``
  * ``setRgb(r, g, b)`` writes the three brightness values with ``analogWrite()`` on **D8** (red), **D7** (green), and **D6** (blue)
  * ``game_feedback(code)`` is a ``switch`` that turns one integer into light and sound: 1 is yellow, 2 is green with two rising tones, 3 is red with one low note, and anything else is off
  * ``successSound()`` plays 880Hz and then 1175Hz with ``tone()``, while ``failureSound()`` plays a single 330Hz note
  * ``Bridge.provide("game_feedback", game_feedback)`` publishes that function so Python is allowed to call it
  * ``loop()`` only pauses — every game event arrives as a Bridge call

**Python (main.py)** — runs on the Linux MPU
  * ``WebUI()`` serves the game page from ``assets/`` and hosts one extra route
  * ``ui.expose_api("GET", "/stream", video_stream)`` answers that route with a ``StreamingResponse`` of ``multipart/x-mixed-replace`` frames, which is what makes the picture move in the browser
  * ``Camera(fps=20)`` and ``loop()`` capture a frame, run ``cv2.flip(frame, 0)`` to turn it upright, and compress it with ``cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])`` into a shared ``current_frame`` under ``frame_lock``
  * ``CloudLLM(...)`` is created twice: ``task_llm`` writes the mission at ``temperature=0.9`` with ``max_tokens=40``, and ``judge_llm`` referees the picture at ``temperature=0.1`` with ``max_tokens=100``
  * ``ui.on_message("new_mission", request_new_mission)`` only starts ``create_mission()`` on a worker thread, so the live preview keeps moving while the mission is being written
  * ``ui.on_message("check_object", check_object)`` refuses to run without a mission (*"Choose NEW MISSION first."*) or without a frame (*"The camera image is not ready yet."*), then copies the newest frame and hands the real work to ``judge_object()`` on another worker thread
  * ``judge_llm.chat(message=prompt, images=[frame])`` is the key call — the mission and the JPEG frame travel together, and ``with_memory(max_messages=0)`` means every judgement is made from the current picture only
  * ``parse_judgement()`` refuses to guess: it requires a ``{...}`` block, parses it with ``json.loads()``, and counts the attempt as a success only when ``success`` is exactly ``True``
  * ``clean_task()`` tidies what the writer returns — quotes and list numbering are stripped, the sentence is forced to begin with *"Find"*, and it is capped at 140 characters
  * ``hardware_feedback(code)`` calls ``Bridge.call("game_feedback", code)``, and ``ui.send_message("game_state", {...}, room=sid)`` reports the mission, the score, the attempts, and the verdict to the browser that asked
  * ``with camera: App.run(user_loop=loop)`` opens the camera before the first frame and runs that loop for as long as the app lives

**Cloud LLM (behind the ``cloud_llm`` brick)** — runs on OpenAI's servers
  * One system prompt makes the model a **mission writer**: one short English mission beginning with *"Find"*, built from a visible property or an everyday purpose such as colour, shape, material, or use — and never about anything sharp, hot, heavy, breakable, dangerous, expensive, private, or alive
  * The other makes it a **fair referee**: judge only what is clearly visible in the supplied image, mark anything that cannot be verified visually as unsuccessful, and answer with one JSON object of the form ``{"success": true, "message": "One short sentence"}``
  * ``temperature=0.9`` keeps the missions varied, while ``temperature=0.1`` keeps the verdicts steady — the same model, tuned for two different temperaments
  * This is the only step that needs the internet, and the only step that costs money

**Bridge** — the channel between the MPU and the MCU
  * Sketch side: ``Bridge.provide("game_feedback", game_feedback)`` exposes the feedback function
  * Python side: ``Bridge.call("game_feedback", code)`` invokes it with one integer
  * The call is wrapped in a ``try``, so a missing sketch only logs a warning — the game keeps playing even if the hardware stays silent
  * One small number is the whole protocol — the model never talks to the chip directly

**Browser (HTML/JS)** — runs in your browser
  * ``socket.emit('new_mission', {})``, ``socket.emit('check_object', {})``, and ``socket.emit('reset_game', {})`` are the three buttons; ``socket.on('connect')`` also sends ``get_state``, so the page opens on the real score instead of a guess
  * ``loadCameraStream()`` sets ``cameraStream.src`` to ``http://<host>:7000/stream?r=<timestamp>``, and the ``error`` listener retries it every 1.5 seconds if the picture drops
  * ``socket.on('game_state', updateState)`` repaints the score board, the mission text, the status panel, and the referee card from the ``state``, ``message``, ``task``, ``score``, ``attempts``, and ``result`` fields
  * ``stateTitles`` gives each state its label — Ready, Creating Mission, Image Captured, AI Referee Is Thinking, Speaking, Success, Try Again, Mission Complete, Error
  * ``updateButtons()`` locks all three buttons while the app is busy or the socket is down, and keeps **CHECK OBJECT** disabled until a mission actually exists
  * ``socket.on('disconnect')`` clears the picture, turns the status dot red, and reports *"Connection to the app was lost."*

Notice that the two model calls never see each other. The writer produces a sentence that ``clean_task()`` has to tame, because a chatty model will happily add quotes, numbering, and hints; the referee produces JSON that ``parse_judgement()`` accepts only on its own strict terms. Both prompts are doing the same job in different clothes: they narrow a model that could answer anything down to an answer this small game can actually use, and the Python code decides what happens when the answer does not fit.

3. Experiment
----------------

**Play Against the Referee**

The referee only knows what is in the frame at the instant you click, so what you show it *is* the experiment. Try each of these and watch the LED, the buzzer, the score, and the referee card at the same time:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - What you do
     - What happens
   * - Click **NEW MISSION** two or three times
     - Each mission is a different sentence, because the prompt carries the last five missions and asks for something new
   * - Show an object that plainly matches
     - The LED turns green, the buzzer plays two rising tones, the score goes up by one, and the referee explains the match
   * - Show an object that clearly does not match
     - The LED turns red, the buzzer plays one low note, the attempts go up by one, and the same mission stays on screen
   * - Show a matching object in dim light, or small in a large frame
     - The verdict can go against you even though the object is right — the prompt tells the referee to mark anything it cannot verify as unsuccessful
   * - Hold up two objects at once, one matching and one not
     - The referee judges only the *main* visible object, so whatever fills the frame decides the outcome
   * - Click **RESET**
     - The score and attempts return to zero, the mission is cleared, and the LED goes out

**Challenge: Trick the Referee**

The prompt asks for a *fair* referee that judges only what is clearly visible, and it says an unclear picture must be marked unsuccessful. Try to make that rule fail. Show an object at the very edge of the frame, or half hidden behind your hand. Show a picture of the required object on a screen instead of the object itself. Ask for a mission that is easy to satisfy in several ways (*"Find something you can write with"* — is a keyboard a valid answer?) and see how the referee decides. Keep a tally of the verdicts that seem right and the ones that seem generous. There is no correct total — the point is to see how much of a judgement the picture really carries, and how much of it the prompt is quietly supplying.

**Challenge: Rewrite the Mission Writer**

The missions come from ``TASK_SYSTEM_PROMPT`` in ``main.py``, and that string is the whole personality of the game. Change it and see what happens to the missions, then to the referee. Ask for missions about one place (*"only objects you would find in a kitchen"*), or about a starting letter, or for missions that are deliberately hard. Then push it the other way and remove the safety sentence — the model will happily invent a mission about a hot kettle or a pet. Put the rule back and watch the missions return to safe, portable objects. Nothing else in the project changes, and yet the whole game does — that is how much power one sentence of instruction carries.

4. Troubleshooting
--------------------

**The status panel says "Choose NEW MISSION first."**

* **Cause:** You clicked **CHECK OBJECT** before a mission existed. The referee has nothing to judge against, so the app stops before it spends a request on the cloud.
* **Solution:** Click **NEW MISSION** and wait for the mission to appear on the card and be spoken. The button is disabled until a mission is in hand, so seeing this message usually means the mission was cleared — by **RESET**, or by a reload of the page.

**The status panel says "The camera image is not ready yet."**

* **Cause:** You clicked **CHECK OBJECT** before the first frame had been captured, so the shared ``current_frame`` was still empty and there was nothing to send to the model.
* **Solution:** Wait until the live view is moving before you check an object. If the preview never starts, fix that first — this message is only about the picture not being there yet, not about the mission or the API key.

**The status panel turns red with "Unable to create a mission..." or "Unable to check the object..."**

* **Cause:** The request to the cloud model failed. Every failure ends up here: no key saved yet, a key that was rejected or has run out of credit, or no internet connection on the board. The message prints the exception type, which is the fastest clue to which of the three it was.
* **Solution:** Check the board's internet connection first, since both models live in the cloud. Then confirm your key is still valid and funded in your OpenAI account, stop the app, and press **Run** again to enter a fresh key. A mission can also fail if the model returns something ``clean_task()`` reduces to nothing, in which case simply ask for another one.

**The referee marks almost everything unsuccessful**

* **Cause:** The judge prompt is deliberately strict: it must mark a result unsuccessful when the required property cannot be verified in the picture. Dim light, a cluttered desk, a small object in a wide frame, or a mission whose wording has several readings all push the verdict towards *no*.
* **Solution:** Fill the frame with one object, hold it still in bright, even light, and check it against a mission that names a visible property (*"Find something red"*) rather than a purpose (*"Find something useful"*). If the missions themselves feel unfair, loosen the wording of ``TASK_SYSTEM_PROMPT`` — the writer and the referee are two separate prompts, and only one of them needs changing.

**The RGB LED changes colour but the buzzer stays silent**

* **Cause:** The LED is on the Bridge path and working, so the feedback call is arriving — the buzzer circuit is the part at fault. The **−** leg is not on **GND**, the **+** leg is not on **D5**, or the legs are the wrong way round for the buzzer you have.
* **Solution:** Re-check the wiring diagram: **+** to **D5** and **−** to **GND**. The sketch drives the buzzer with ``tone()``, which works for both an active and a passive buzzer, so either type is fine. If the LED and the buzzer both do nothing, the sketch is not running — stop the app and press **Run** again so both halves restart together.

**The live camera picture never appears, or the card is silent while it should be speaking**

* **Cause:** Two separate one-time setups. No frames mean the camera is not running — external carriers were never enabled, the camera type for the connector was not selected, or the ribbon cable is not fully seated. Silence from the speaker usually means the TTS runtime is still downloading and preparing itself on first use.
* **Solution:** For the camera, complete the one-time setup at :ref:`enable_external_carriers`, choosing the type that matches the connector your camera is plugged into, then let the board reboot and run the app again. For the speaker, give the first run the half hour it may need to finish preparing the TTS runtime, and keep the board online. The game itself keeps working either way — a missing camera reports *"The camera image is not ready yet."*, and a failed ``tts.say()`` is caught and logged without stopping play.

5. Summary
-------------

You just built a game that writes its own rules and then judges you by them. The board invents a mission, speaks it aloud, watches you through the camera, and answers with colour, sound, and a score — and the only thing that changed between the two model calls was the sentence of instruction wrapped around each one.

* A single model can play two roles at once: ``task_llm`` writes the mission at ``temperature=0.9``, while ``judge_llm`` referees it at ``temperature=0.1``
* **Structured output** turns an opinion into data — the referee is told to answer with ``{"success": true, "message": "..."}``, and ``parse_judgement()`` accepts the verdict only when that JSON parses and ``success`` is exactly ``True``
* The same one-integer Bridge protocol as the earlier projects is enough for a whole game: 1 yellow, 2 green with two rising tones, 3 red with one low note, 0 off
* One shared state object — mission, score, attempts, result — means the page, the referee card, and the status panel can never disagree
* Both halves of the exchange run on worker threads, so the live preview keeps moving while the model thinks, and the ``busy`` flag keeps exactly one request in flight

The next project puts the model on the other side of the desk. Instead of writing a mission and judging an object, it will write the quiz questions *and* decide whether your answers are correct — so the intelligence that checks you is the same intelligence that set the test. Everything you built here is the groundwork: two prompts with two jobs, a shared game state, and a board that reacts the moment the verdict arrives.
