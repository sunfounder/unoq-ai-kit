07 AI Quiz Show
====================

.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

The board has listened to you, argued with you, pulled a face, and looked at the world. Now it takes the teacher's chair. Ask it for a question and it writes one on the spot — three choices, one correct answer, and a short explanation — then reads the whole thing aloud. You answer with a button on the page, and the verdict arrives all at once: a coloured light, a buzzer tone, a spoken sentence, and a point on the scoreboard. The clever part is not that the model writes the question; it is that the model is asked for *data* rather than a paragraph, so every field the page needs already has a name before a single word reaches the browser.

In this lesson, you will learn to:

* Ask a cloud model for **structured data** — a question, three choices, the correct letter, and an explanation — instead of a sentence your code cannot use
* Pull JSON out of a model's reply and validate every field before it is allowed on screen
* Turn one small integer into feedback on three different outputs at once: an RGB colour, a buzzer tone, and a spoken sentence
* Keep the score and the number of answered questions on the board, and restore them when a browser reloads
* Keep a whole round down to a single cloud request by comparing the answer locally

1. Setup
-----------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_rgb_led` (common cathode)
     - 3 * :ref:`cpn_resistor` (220Ω)
     - 1 * :ref:`cpn_buzzer` (passive)
   * - |list_pan_tilt|
     - |list_rgb_led|
     - |list_220ohm|
     - |list_passive_buzzer|
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

* ``web_ui`` — serves the quiz page and carries every message between the browser and Python
* ``cloud_llm`` — asks a cloud language model for a new question and returns the JSON behind it
* ``sunfounder_tts`` — reads the question, the three choices, and the explanation aloud on the board's speaker

Because the model is reached over the internet, the project needs a key of your own. ``app.yaml`` declares the ``cloud_llm`` brick with an empty ``API_KEY``, so App Lab asks you for an **OpenAI API key** the first time you press **Run** and stores it for you.

The sketch declares no external libraries: ``sketch.yaml`` has no ``libraries:`` section at all, because the Bridge library that lets Python call the sketch is part of the UNO Q core and needs no installation.

**Wiring Diagram**

The RGB LED's red, green, and blue anodes go to **D8**, **D7**, and **D6**, each through its own **220Ω** resistor, and the longest leg — the **common cathode** — goes to **GND**; the passive buzzer's **+** leg goes to **D5** and its **−** leg to **GND**.

.. image:: /img/wiring/wiring_pc_buzzer_rgb.png
   :width: 600
   :align: center

.. note::

   The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.


2. Run the App
----------------

#. Download :download:`07 AI Quiz Show.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/07.AI.Quiz.Show.zip>`.
#. Open **Arduino App Lab** and go to **Apps**. Click the dropdown arrow next to **Create new app +** and select **Import App**.

   .. image:: /img/app_import_app.png
      :width: 600

#. Select **Import from Computer**.

   .. image:: /img/app_import_pc.png
      :width: 600

#. Choose the package you downloaded. The app appears in **Apps** — click it to open.
#. Wire the RGB LED and the passive buzzer as the diagram shows, then connect the board and click the **Run** button (▶) in the top-right corner. The sketch is flashed to the board and Python starts the Web UI; the RGB LED stays dark until the first question is created, because this sketch has no colour self-test.

   .. image:: /img/app_run.png
      :width: 500
      :align: center

   .. note::

      The first time you run this project, App Lab asks for your **OpenAI API key**, because the app uses the ``cloud_llm`` brick to reach the model. Paste a key from your OpenAI account and save it — App Lab keeps the key for your board, so you only do this once.

#. The Output window prints *"AI Quiz Show ready."* and a **Web UI** tab opens by itself. The status row reads **Connecting** for a moment, then **Connected** with a blue dot.
#. The page shows the score board first — **Score 0**, **Answered 0**, and a greyed-out **RESET** — then the question card, the three choice buttons each showing a dash, the status panel reading *"Choose NEW QUESTION to begin."*, the **NEW QUESTION** button, and the explanation card with *"The explanation will appear here."*
#. Click **NEW QUESTION**. The status panel walks through its stages — **Creating Question** while the model writes, then **Reading Question** while the voice reads the question and all three choices aloud — and only then does it settle on **Ready**. The RGB LED glows yellow the moment the question has arrived, and the three buttons unlock when the reading has finished.
#. Read the choices and click **A**, **B**, or **C**. A correct answer turns the LED green, plays two rising tones, and shows **Correct!** with a point added to the score; a wrong answer turns the LED red, plays one low tone, and tells you which letter was right. Either way the explanation lands in the **Answer Explanation** card and is read aloud, and the panel finishes on *"Choose NEW QUESTION to continue."*
#. Play a few rounds, then try **RESET** to clear the scoreboard, and **NEW QUESTION** whenever you want another one. The page looks like this — the score and answered counters at the top, the question and its three choices in the middle, and the explanation at the bottom.

   .. image:: img/ai_quiz_show.png
      :width: 600
      :align: center

**How it Works**

Here is the whole path a round travels — a request out to the model, a question onto the page, and one click that comes back as light, sound, and speech.

An App Lab project is a folder of files. Here is what is inside this one:

* ``07 AI Quiz Show/`` — the app folder

  * ``app.yaml`` — app metadata: name, icon, and the three Bricks the project declares
  * ``README.md`` — a short guide to the project

  * ``python/``

    * ``main.py`` — the question request, the JSON parsing, the scoring, and the Bridge calls

  * ``sketch/``

    * ``sketch.ino`` — the RGB and buzzer pins, the two tone patterns, and the ``quiz_feedback()`` function
    * ``sketch.yaml`` — sketch configuration for the UNO Q board

  * ``bricks/``

    * ``sunfounder_tts/`` — the text-to-speech brick the app ships with: the local voice server behind ``tts.say()``

  * ``assets/``

    * ``index.html`` — the quiz page: score board, question card, three choice buttons, status panel, and explanation card
    * ``app.js`` — browser logic: the socket events, the button locking, and the panel repainting
    * ``style.css`` — the visual styling of the page
    * ``libs/socket.io.min.js`` — the Socket.IO client that carries messages between the page and the board
    * ``img/sf_logo.png`` — the logo in the page header
    * ``docs_assets/`` — the wiring and result images used by this documentation

The data path, from a click on **NEW QUESTION** to a verdict you can hear:

.. mermaid::

   sequenceDiagram
       participant B as Browser (HTML/JS)
       participant P as Python (main.py)
       participant L as Cloud LLM (gpt-4o-mini)
       participant S as Sketch (sketch.ino)
       participant T as Speaker (sunfounder_tts)

       B->>P: socket.emit("new_question")
       P->>L: llm.chat(prompt) - ask for one quiz JSON
       L-->>P: question, choices A B C, answer, explanation
       P->>P: parse_quiz() - validate every field
       P->>S: Bridge.call("quiz_feedback", 1)
       S->>S: setRgb(255, 160, 0) - yellow, waiting
       P->>T: tts.say(question and the three choices)
       P-->>B: socket "quiz_state" - ready
       B->>P: socket.emit("submit_answer", answer)
       P->>P: selected == quiz["answer"]
       P->>S: Bridge.call("quiz_feedback", 2 or 3)
       S->>S: green and two tones, or red and one low tone
       P-->>B: socket "quiz_state" - correct or wrong
       P->>T: tts.say(the explanation)

Here is what each piece does:

**Sketch (sketch.ino)** — runs on the STM32 MCU
  * ``setup()`` sets **D5**, **D6**, **D7**, and **D8** to outputs, blanks the LED with ``setRgb(0, 0, 0)``, then calls ``Bridge.begin()``
  * ``setRgb(r, g, b)`` writes the three channels with ``analogWrite()`` on **D8** (red), **D7** (green), and **D6** (blue)
  * ``quiz_feedback(code)`` is a ``switch`` that turns one integer into a whole mood: 1 yellow for waiting, 2 green plus ``correctSound()``, 3 red plus ``wrongSound()``, anything else off
  * ``correctSound()`` plays two rising tones with ``tone(BUZZER_PIN, 880, 100)``, a short ``delay(130)``, then a 1175 Hz tone of 160 ms — and ``wrongSound()`` answers a wrong choice with a single low 330 Hz tone
  * The four codes are the sketch's entire vocabulary: 0 for a reset, 1 for a question waiting, 2 for a correct answer, and 3 for a wrong answer or a failed request
  * ``Bridge.provide("quiz_feedback", quiz_feedback)`` publishes that function so Python is allowed to call it, and ``loop()`` does nothing but ``delay(10)``

**Python (main.py)** — runs on the Linux MPU
  * ``WebUI()`` serves the quiz page from ``assets/``, and ``ui.on_message("new_question", request_question)`` together with ``submit_answer`` and ``reset_quiz`` listens for the three things the page can send
  * ``CloudLLM(model="openai:gpt-4o-mini", system_prompt=QUIZ_SYSTEM_PROMPT, temperature=0.8, max_tokens=180)`` creates the link to the model and fixes its behaviour up front
  * ``request_question()`` refuses a second request while ``busy`` is set and hands the slow work to ``threading.Thread(target=create_question, ...)``, so the page stays responsive while the model thinks
  * ``llm.chat(message=prompt)`` asks for one question, and ``parse_quiz()`` pulls the first curly-braced block out with a regular expression, runs ``json.loads()`` on it, normalises the whitespace, and refuses anything with a missing choice or an answer letter that is not one of A, B, or C
  * The parser also repairs what it can: an empty explanation is replaced with *"The correct answer is X: ..."*, and the question, each choice, and the explanation are trimmed to 180, 100, and 180 characters so nothing spoken runs away from the reader
  * ``llm.with_memory(max_messages=0)`` keeps every round independent, and the prompt carries the last five questions back with *"Do not repeat these questions"*
  * ``hardware_feedback(code)`` wraps ``Bridge.call("quiz_feedback", code)`` in a ``try``/``except`` so a missing sketch can never break a round, and it reports the failure in the log instead
  * ``tts.say(...)`` reads the question and its three choices, and ``send_state()`` builds one payload — the state, the message, the current quiz, the score, the answered count, ``answered``, ``selected``, and ``result`` — before ``ui.send_message("quiz_state", payload, room=sid)`` returns it to the one browser that asked
  * ``process_answer()`` compares the chosen letter with ``quiz["answer"]``, updates ``score`` and ``questions_answered`` under ``state_lock``, and only then speaks — the answer is checked locally, so a round costs exactly one cloud request
  * ``reset_quiz()`` clears the score, the counter, and the current question, but it refuses to do any of it mid-round while ``busy`` is set
  * ``App.run()`` starts the app and keeps it alive

**Cloud LLM (behind the ``cloud_llm`` brick)** — runs on OpenAI's servers
  * The **system prompt** makes it a quiz writer for students: varied general-knowledge topics, exactly three choices with exactly one correct answer, and no trick questions, politics, violence, adult topics, or time-sensitive facts
  * It insists on one JSON object with a fixed shape — ``question``, ``choices``, ``answer``, and ``explanation`` — so the code always knows which fields to expect
  * The reply is ordinary text that merely happens to contain JSON, so ``parse_quiz()`` searches for the first ``{...}`` block; a stray sentence around the object does no harm, but a reply with no object at all is refused as *"The AI did not return quiz JSON."*
  * ``temperature=0.8`` keeps the questions varied while ``max_tokens=180`` keeps them short enough to read aloud, and ``with_memory(max_messages=0)`` makes sure no earlier round leaks into the next one
  * This is the only step that needs the internet, and the only step that costs money — everything after it, including the scoring, happens on the board

**Bridge** — the channel between the MPU and the MCU
  * Sketch side: ``Bridge.provide("quiz_feedback", quiz_feedback)`` exposes the feedback function
  * Python side: ``Bridge.call("quiz_feedback", code)`` invokes it with one integer
  * The entire protocol is a single number — 0 reset, 1 waiting, 2 correct, 3 wrong — so the model's words never travel to the chip, only the verdict does
  * If the sketch is missing or the name does not match, the wrapper logs a warning and the quiz plays on, which is why the Web UI never depends on the hardware being there

**Speaker (sunfounder_tts)** — runs on the board
  * ``EdgeTTS()`` with ``set_voice("en-US-JennyNeural")`` and ``set_volume(50)`` prepares the voice, and ``tts.say(...)`` speaks a finished sentence
  * The question is read with its three choices in order, so a player watching the LED still hears the whole round; the explanation is spoken after the verdict
  * Spoken text and on-screen text always come from the same payload, so the voice can never announce an answer the page disagrees with

**Browser (HTML/JS)** — runs in your browser
  * ``socket.emit('new_question', {})``, ``socket.emit('submit_answer', {answer})``, ``reset_quiz``, and ``get_state`` are the only messages the page sends
  * ``socket.on('quiz_state', updateState)`` repaints everything from one payload: the question card, the three choice labels, the score, the answered count, and the status panel
  * ``stateTitles`` gives each state its label — Ready, Creating Question, Reading Question, Correct, Not Quite, Question Complete, Error
  * ``updateState()`` marks the chosen button green or red with ``correct-choice`` and ``wrong-choice``, and ``updateButtons()`` keeps every button disabled while the app is ``busy`` — which is what stops a second answer during a round
  * ``socket.on('connect')`` asks for ``get_state`` so a reloaded page shows the round in progress, while ``socket.on('disconnect')`` turns the dot red and locks the buttons

Notice how much of this quiz is ordinary bookkeeping. The model supplies the words, but Python supplies the shape: a fixed set of fields, three choices that must all be present, an answer letter that must be one of them, one question at a time, and a score that only ever moves inside ``state_lock``. The model is free to be creative about *what* it asks; your code decides what is allowed to become a question on the page. And that division of labour is why a bad round is never a dead end — a malformed reply becomes a message in the status panel, and **NEW QUESTION** starts again from nothing.

3. Experiment
----------------

**Play Faster Than the Voice**

Every round is the same three stages — asking, reading, answering — so the fun is in the timing. Try each of these and watch the panel, the LED, and the buzzer at the same time:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - What you do
     - What happens
   * - Click **NEW QUESTION** and wait
     - The panel walks **Creating Question** → **Reading Question** → **Ready**, and the RGB LED turns yellow as soon as the question has arrived
   * - Click **A**, **B**, or **C** while the question is still being read
     - Nothing moves — the buttons stay disabled on purpose, because a round you could answer before hearing it would not be much of a quiz
   * - Click the correct choice
     - The LED turns green, the buzzer plays two rising tones, the panel reads **Correct!**, the score goes up by one, and the explanation appears and is read aloud
   * - Click a wrong choice
     - The LED turns red, the buzzer plays one low tone, the panel tells you which letter was right, and the explanation still arrives
   * - Answer one question twice
     - Impossible — Python sets ``answered`` the instant you click, so a second ``submit_answer`` for the same question is ignored
   * - Click **RESET** between rounds
     - The score and the answered count return to 0, the LED goes dark, and the panel reads *"Score reset. Choose NEW QUESTION to begin."*
   * - Reload the page in the middle of a round
     - The dot returns to **Connected** and ``get_state`` restores the current question and score straight from Python

**Read the Panel, Not Just the Light**

Every state this app can be in has a name, and the panel always shows it, so the fastest way to understand the quiz is to read the panel instead of guessing from the light:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - What the panel says
     - What the app is doing
   * - **Ready**
     - A question is loaded and unanswered. The three choices are live.
   * - **Creating Question**
     - Python is waiting for the model to return the JSON. Everything is locked.
   * - **Reading Question**
     - The question and its three choices are being spoken. Still locked.
   * - **Correct!** or **Not Quite**
     - The verdict is on screen, the LED and the buzzer have fired, and the explanation is arriving.
   * - **Question Complete**
     - The round is over and the score has been counted. Press **NEW QUESTION** for the next one.
   * - **Error**
     - The round failed, almost always at the cloud request. The message names the exception that caused it.

The titles come straight from ``stateTitles`` in ``app.js``, and each one names a state Python really sends with ``send_state(...)``, so the panel is a faithful map of what the board is doing rather than decoration.

**Challenge: Catch the AI Out**

The model writes the question *and* marks the answer itself, and nothing between the two checks whether that answer is actually correct. ``parse_quiz()`` only checks the shape of the reply: three non-empty choices, and an answer letter that matches one of them. It never checks the truth. So play a few rounds in a subject you know well — sport, a language, a country's capital cities — and keep a tally of how often the marked answer is right. Then look for the harder question: is the *question* itself fair, or has the model written something ambiguous enough that two choices could be defended? Note how confident the explanation sounds either way. A structured reply is not the same thing as a factually correct one, and this project shows the difference better than any of the earlier ones.

**Challenge: Play With the Screen Covered**

The voice reads the question and then the three choices in order, so a whole round is answerable with your eyes closed. Cover the page — or turn the screen away — and play five rounds from sound alone. Which parts are easy to follow, and where does hearing the choices become confusing? Then try to improve it: the sentence is built in ``main.py`` just before ``speak()`` is called, so you can make it repeat the question between choices, or say *"Choice A is ..."* instead of the bare letter. Look back at the screen only to check the score. It is a change to a single string, and it is exactly the kind of tuning that decides whether a spoken interface is usable.

**Challenge: Reshape the Prompt, Then Reshape the Code**

The system prompt is where the model's freedom lives, so start there. Set ``temperature=0.2`` and play a few rounds — do the questions get more predictable? Then edit ``QUIZ_SYSTEM_PROMPT`` to name a single topic (*space*, *animals*, *everyday science*) and see how quickly the game narrows. Finally, try the change the code cannot absorb: ask for **four** choices instead of three. Watch what happens when the model returns a ``"D"`` that ``parse_quiz()`` never asked for, then work out everything you would have to touch to support it — the prompt, the validator, the choice buttons in ``index.html``, and the state map in ``app.js``. That list is the honest answer to how much structure this app really has, and how much of it you would have to widen to change the game.

4. Troubleshooting
--------------------

**The status panel turns red with "Unable to create a question: ..."**

* **Cause:** The cloud request failed, or the reply could not be turned into a question. Every failure ends up here: no key saved yet, a key that was rejected or has run out of credit, no internet connection on the board, or a model reply that contained no JSON at all. The message names the exception type, which is the fastest clue to which of these it was.
* **Solution:** Check the board's internet connection first, since the model lives in the cloud, then confirm your key is still valid and funded in your OpenAI account, stop the app, and press **Run** again to enter a fresh key. Note that this error state also lights the LED red and plays the low tone, so a red LED with one low beep when you have not answered anything is a failed request rather than a wrong answer — just click **NEW QUESTION** to try again.

**The A/B/C buttons stay greyed out**

* **Cause:** The buttons are locked until the app has a question *and* is no longer busy. ``app.js`` disables them while the state is ``generating``, ``speaking``, ``correct``, or ``wrong``, while no question is loaded, and after a question has already been answered.
* **Solution:** Watch the status panel rather than the buttons. **Ready** with the question on screen means they are live. If the panel never reaches **Ready**, the reading is still running — or the TTS runtime is still being prepared on the first run, which is the one case that can take a very long time.

**The LED shows yellow but never turns green or red**

* **Cause:** The Bridge call is not reaching the sketch. ``hardware_feedback()`` catches that failure and only writes *"Hardware feedback unavailable"* to the log, so the quiz carries on with no light or sound at all.
* **Solution:** Make sure ``Bridge.provide("quiz_feedback", quiz_feedback)`` in the sketch matches ``Bridge.call("quiz_feedback", code)`` in Python exactly — the names are case-sensitive. Unlike the light control project earlier, this sketch has no colour self-test, so the quickest check is to press **RESET** (code 0, LED off) and then **NEW QUESTION** (code 1, yellow) and see whether either has any effect.

**The buzzer stays silent while everything else works**

* **Cause:** The wrong kind of buzzer, or a loose leg. This project needs a **passive** buzzer, because the sketch generates the tones itself with ``tone()`` — an active buzzer only ever makes its own fixed sound and will not follow those frequencies.
* **Solution:** Fit the passive buzzer with its **+** leg on **D5** and its **−** leg on **GND**, and press it down until both legs are firmly in the breadboard. The tones are deliberately short — 100 ms and 160 ms for a correct answer, 250 ms for a wrong one — so listen closely rather than expecting a long alarm.

**The question appears on the page but is never read aloud**

* **Cause:** Either the TTS runtime is still being prepared on the first run, or the voice failed and ``speak()`` swallowed the error with a *"TTS unavailable"* log line. The quiz itself is unaffected, which is why only the audio disappears.
* **Solution:** On the very first run, let the one-time TTS setup finish — keep the board online and wait it out. After that, check that the speaker is connected and that the app has not been stopped mid-round. The question is always on the page as well, so you can keep playing while you investigate.

5. Summary
-------------

You just built a quiz show that writes its own questions. The board asks a cloud model for structured data, checks that the data makes sense, reads it out loud, judges your answer, and reports the verdict through an LED, a buzzer, a voice, and a scoreboard — all from a single click on the page.

* Asking for **JSON** instead of prose is what turns a chat reply into data — one ``json.loads()`` and the question, the choices, the answer, and the explanation become fields your program can use
* ``parse_quiz()`` is the gate: a missing choice or an answer letter that is not one of the choices is refused outright, so a malformed reply becomes a message on screen instead of a broken round
* The answer is checked locally with ``selected == quiz["answer"]``, so a round costs exactly one cloud request and the score never depends on the network
* One tiny integer carries the whole verdict to the hardware — ``Bridge.call("quiz_feedback", code)`` drives the RGB colour and the buzzer pattern from a single ``switch``
* Score, answered count, and the current question all live in Python behind ``state_lock``, so a browser that reloads asks for ``get_state`` and picks the round up where it left off

The next project hands the model something far less tidy than a scoreboard: the camera. You will roll a set of story dice, photograph what they show, and listen while the model turns that picture into a narrated story — the same three pieces you have used all along, an input on the board, a model for judgement, and a page that shows you what happened.

