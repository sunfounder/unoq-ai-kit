03 AI Environment Advisor
=========================

.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

So far the board has always answered the same question: *what is the number right now?* A slider value, a temperature, a light reading — your code measured it and your page printed it. This project adds the missing half. The DHT11 and the photoresistor you have already used take the measurement, and a **large language model** reads those three numbers as a description of a room, decides whether the room is comfortable, warm, humid, dark, or something in between, and writes a short sentence of practical advice next to it.

In this lesson, you will learn to:

* Send live sensor readings — not just a sentence you typed — to a large language model
* Ask the model for a **structured answer**, so the reply arrives as fields your page can place instead of a paragraph it has to guess at
* Guard that answer on your own side: check the status against a known list, and fall back to something safe when the reply cannot be read
* Follow a third kind of Bridge call, where the sketch pushes data to Python with ``Bridge.notify()`` instead of waiting to be asked
* See the difference between a **measurement** (the number the sensor gives) and an **interpretation** (what that number means for a person in the room)

1. Setup
-----------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_humiture_sensor` (DHT11)
     - 1 * :ref:`cpn_photoresistor` (Photoresistor Module)
     - 1 * USB-C Cable
   * - |list_pan_tilt|
     - |list_dht11|
     - |list_photoresistor|
     - |list_usb_cable|
   * - Several :ref:`cpn_wires`
     -
     -
     -
   * - |list_wire|
     -
     -
     -

**Software Requirements**

This project uses two App Lab **Bricks** — support packages that App Lab adds to your app for you:

* ``web_ui`` — serves the advisor page and carries the live readings and the model's answer between the browser and Python
* ``cloud_llm`` — sends the reading summary to a cloud language model and streams the advice back

Because the model is reached over the internet, the project needs a key of your own. ``app.yaml`` declares the ``cloud_llm`` brick with an empty ``API_KEY``, so App Lab asks you for an **OpenAI API key** the first time you press **Run** and stores it for you.

The sketch needs two libraries, both declared in ``sketch.yaml`` and installed for you when the app is built:

* ``DHT sensor library (1.4.6)`` — the ``DHT`` class that reads temperature and humidity from the sensor
* ``Adafruit Unified Sensor (1.1.15)`` — the shared sensor interface that the DHT library is built on

The Bridge library that lets the sketch and Python talk to each other is part of the UNO Q core, so there is nothing else to install.

**Hardware Check**

#. Power the board down before you move any wires — both sensors sit on the 5V rail.
#. Plug the **DHT11** into its cable, then run the three wires to the Robot Shield: **VCC** to **5V**, **GND** to **GND**, and **DATA** to **D4**. The DATA line carries the whole measurement, so it must be a firm connection.
#. Plug the **photoresistor module** in next to it and run its three wires the same way: **VCC** to **5V**, **GND** to **GND**, and its signal pin to **A0**.
#. Space the two sensors apart. The DHT11 reports the air around it, so a photoresistor module pressed against it, or a hand cupped over it, will change what the temperature reading means.
#. Plug the **USB-C cable** into the UNO Q and your computer, and check that the board powers up.

**Wiring Diagram**

The **DHT11** uses three pins — **DATA** to **D4**, **VCC** to **5V**, **GND** to **GND** — and the **photoresistor module** uses the same three connections with its signal pin on **A0**. The light reading is a *relative* classroom measurement taken from the voltage on **A0**, so it depends on how the module is built: on most modules the percentage rises as the room gets brighter, but on a module whose resistor and photoresistor are swapped it will rise as the room gets darker instead. Compare the number with the room you are sitting in — if it moves the wrong way, that is the module, not a mistake in your wiring.

.. image:: /img/wiring/wiring_dht11.png
   :width: 500
   :align: center

2. Run the App
----------------

#. Download :download:`03 AI Environment Advisor.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/03.AI.Environment.Advisor.zip>`.
#. Open **Arduino App Lab** and go to **Apps**. Click the dropdown arrow next to **Create new app +** and select **Import App**.

   .. image:: /img/app_import_app.png
      :width: 600

#. Select **Import from Computer**.

   .. image:: /img/app_import_pc.png
      :width: 600

#. Choose the package you downloaded. The app appears in **Apps** — click it to open.
#. With the app open, click the **Run** button (▶) in the top-right corner. The sketch gives the DHT11 two seconds to settle, takes its first reading, and the Python side starts the Web UI.

   .. image:: /img/app_run.png
      :width: 500
      :align: center

   .. note::

      The first time you run this project, App Lab asks for your **OpenAI API key**, because the app uses the ``cloud_llm`` brick to reach the model. Paste a key from your OpenAI account and save it — App Lab keeps the key for your board, so you only do this once.

#. The Output window prints *"AI Environment Advisor ready — waiting for sensor data."* and a **Web UI** tab opens by itself. The status row reads **Connected** with a blue dot.
#. Watch the three cards at the top of the page. Temperature and humidity update every two seconds, and the light card shows a percentage with a word underneath it — **Dark**, **Dim**, **Bright**, or **Very Bright**.
#. Once real readings appear, the **Analyze Environment** button becomes clickable. Press it, and the status row switches to **Analyzing** while the model reads the current snapshot. A moment later the panel fills in: a status word, a one-sentence summary, and a suggestion in its own box.
#. Leave the page open for a while. The sensor cards keep updating the whole time — you can press **Analyze Environment** again whenever the room has changed and compare the two pieces of advice.

   .. image:: img/environment_advisor.png
      :width: 600
      :align: center

**How it Works**

Here is the whole path a reading travels — from two sensors on the breadboard, up through Python to the cloud, and back to the page as advice.

An App Lab project is a folder of files. Here is what is inside this one:

* ``03 AI Environment Advisor/`` — the app folder

  * ``app.yaml`` — app metadata: name, icon, and the two Bricks the project declares
  * ``README.md`` — a short guide to the project

  * ``python/``

    * ``main.py`` — the live reading store, the prompt, the reply parser, and the model request

  * ``sketch/``

    * ``sketch.ino`` — the DHT11 and photoresistor code, the two-second timer, and the Bridge notifications
    * ``sketch.yaml`` — sketch configuration and the two libraries it needs

  * ``assets/``

    * ``index.html`` — the advisor page: status row, three sensor cards, analysis panel, and button
    * ``app.js`` — browser logic: live readings, the Analyze button, and drawing the model's answer
    * ``style.css`` — the visual styling of the page
    * ``libs/socket.io.min.js`` — the Socket.IO client that carries messages between the page and the board
    * ``img/sf_logo.png`` — the logo in the page header
    * ``docs_assets/`` — the result and wiring images used by this documentation

The data path, from a sensor voltage to a sentence of advice:

.. mermaid::

   sequenceDiagram
       participant S as Sketch (sketch.ino)
       participant P as Python (main.py)
       participant B as Browser (HTML/JS)
       participant L as Cloud LLM (OpenAI)

       S->>S: dht.readTemperature() and analogRead(A0)
       S->>P: Bridge.notify("environment_update", t, h, raw)
       P->>P: light_description(percent) and latest_environment.update()
       P-->>B: ui.send_message("sensor_update", latest_environment)
       B->>P: socket.emit("analyze_environment", {})
       P->>L: llm.chat_stream(message=prompt)
       L-->>P: {"status": "...", "summary": "...", "suggestion": "..."}
       P->>P: parse_analysis(raw_response) and VALID_STATUSES check
       P-->>B: ui.send_message("analysis_result", analysis)
       B->>B: analysisStatus / analysisSummary / analysisSuggestion

Here is what each piece does:

**Sketch (sketch.ino)** — runs on the STM32 MCU
  * ``setup()`` sets **A0** to an input, calls ``dht.begin()``, then calls ``Bridge.begin()`` so Python can be notified
  * After two seconds of settling time it takes the first reading immediately, so the page has data as soon as it opens
  * ``sendEnvironmentData()`` reads ``dht.readHumidity()`` and ``dht.readTemperature()``, and if either comes back as ``isnan()`` it reports a failure instead of sending nonsense
  * ``analogRead(LIGHT_SENSOR_PIN)`` reads the photoresistor on **A0** and hands the raw value to Python, which does the arithmetic
  * ``Bridge.notify("environment_update", temperature, humidity, lightRaw)`` pushes the three values to Python — nothing was asked for, the sketch sends them on its own
  * ``loop()`` runs a ``millis()`` timer and calls ``sendEnvironmentData()`` once every two seconds, then sleeps for ten milliseconds

**Python (main.py)** — runs on the Linux MPU
  * ``WebUI()`` starts the server that hands the advisor page from ``assets/`` to your browser
  * ``Bridge.provide("environment_update", environment_update)`` registers the function the sketch notifies — the mirror image of the ``Bridge.call()`` you have used before
  * ``environment_update(temperature, humidity, light_raw)`` clamps the raw value between 0 and 1023, converts it to a percentage, and stores all five fields in ``latest_environment``
  * ``light_description(percent)`` turns that percentage into a word: below 25 is **Dark**, below 55 is **Dim**, below 80 is **Bright**, and anything higher is **Very Bright**
  * ``ui.send_message("sensor_update", latest_environment)`` pushes the stored readings out to every open page, and ``request_state()`` sends them again whenever a new browser connects
  * ``analyze_environment()`` refuses to do anything until the temperature is no longer ``None``, then sends ``analysis_status`` so the page can show **Analyzing**
  * The prompt is built from a single snapshot — one temperature, one humidity, one light percentage — so the model always judges a consistent moment
  * ``CloudLLM(model="openai:gpt-4o-mini", system_prompt=SYSTEM_PROMPT)`` creates the link to the cloud model and fixes its behaviour up front
  * ``"".join(llm.chat_stream(message=prompt))`` sends the snapshot and collects the streamed answer into one string
  * ``parse_analysis()`` is the safety net: it strips any stray code fences, pulls out the outermost ``{...}`` with a ``re.search()``, and if ``json.loads()`` still fails it returns a **Mixed** answer asking you to try again
  * ``VALID_STATUSES`` holds the eight words the model is allowed to use, and anything outside that set quietly becomes ``mixed``
  * ``ui.send_message("analysis_result", analysis)`` sends the final status, summary, and suggestion back to the page
  * ``App.run()`` starts the app and keeps it alive

**Cloud LLM (behind the ``cloud_llm`` brick)** — runs on OpenAI's servers
  * The **system prompt** explains that the model is an environment advisor for a classroom, forbids medical certainty, and lists the eight statuses it may choose from
  * It also demands the answer arrive as JSON with exactly three fields — ``status``, ``summary``, and ``suggestion`` — with no Markdown and nothing outside the JSON
  * Your readings and that instruction travel over the internet together, and only the model's answer comes back; the board never sends anything but those three numbers
  * Only this step needs the internet — the sensors, the sketch, the page, and the readings all stay on your desk

**Bridge** — the channel between the MCU and the MPU
  * Sketch side: ``Bridge.notify("environment_update", temperature, humidity, lightRaw)`` sends three values without being asked
  * Sketch side: ``Bridge.notify("sensor_error", ...)`` sends a message instead of readings when the DHT11 cannot be read
  * Python side: ``Bridge.provide("environment_update", environment_update)`` says which Python function receives them, and the same for ``sensor_error``
  * Because the sketch starts the conversation, the readings arrive on their own twice a second rather than waiting for a request

**Browser (HTML/JS)** — runs in your browser
  * ``socket.on('sensor_update', ...)`` writes the temperature, humidity, and light percentage into the three cards, and ignores any message where temperature or humidity is still ``null``
  * ``socket.on('connect')`` emits ``request_state`` so a page that opens late still gets the current readings immediately
  * ``analyzeButton.addEventListener('click', ...)`` emits ``analyze_environment`` — but only when readings have arrived and no analysis is already running
  * ``socket.on('analysis_result', ...)`` fills ``analysisStatus``, ``analysisSummary``, and ``analysisSuggestion`` with the three fields the model returned
  * ``socket.on('analysis_status', ...)`` and ``setAnalyzing()`` swap the button to **Analyzing…** and disable it while the request is in flight
  * ``showError()`` fills the error banner for both ``sensor_error`` and ``analysis_error``, so a wiring problem and a model problem are both visible on the page
  * ``socket.on('disconnect')`` turns the status dot red and stops the spinner, so a stopped app never looks like it is still thinking

Notice that the model never touches a pin. It receives three numbers that Python has already checked and labelled, and it returns three pieces of text that Python checks again before your page is allowed to show them. The interesting split is that Python decides what the light *is* — a hard percentage and a fixed word — while the model decides what the light *means* for the person in the room. One is arithmetic, the other is judgement, and this project needs both.

3. Experiment
----------------

**Change the Room, Change the Advice**

The model only ever sees the snapshot you send it, so the fastest way to understand this project is to change the room and press **Analyze Environment** again. Keep the page open and watch both the sensor cards and the advice panel:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - What you do
     - What the advice becomes
   * - Cover the photoresistor with your hand and wait for the light card to drop under 25
     - The light card reads **Dark** and the model's status is likely **Dark**, with a suggestion about turning on a lamp or opening the curtains
   * - Shine a phone torch at the photoresistor until the card passes 80
     - The card reads **Very Bright** and the status is likely **Bright**, with a suggestion about glare, shade, or saving energy
   * - Breathe warm air onto the DHT11 for a few seconds
     - The temperature climbs and the humidity jumps, and **Humid** becomes a likely status, with advice about ventilation
   * - Hold an ice pack or a cold drink near the DHT11 without touching it
     - The temperature falls and the status moves towards **Cold**, with advice about heating or a warmer layer
   * - Leave the room alone and press Analyze twice, a minute apart
     - The numbers barely move, so you often get the same status twice — proof that the model is answering the snapshot, not inventing a new opinion each time
   * - Cover the photoresistor and warm the DHT11 at the same time
     - The readings pull in different directions, and **Mixed** — the status the code also uses when a reply cannot be read — is a likely answer

**Challenge: Make the Advice Change Your Mind**

Try to find a set of readings where the model's advice is genuinely useful rather than obvious — a combination where the raw numbers alone would not tell you what to do. Aim for a room that is mildly uncomfortable in two ways at once: a little too warm *and* a little dark, or slightly humid *and* very bright. Ask yourself what advice you would give from the three numbers alone, then press Analyze and compare. When the model's answer is better than yours, what extra thing did it know? When it is worse, what did the three numbers leave out — air movement, the time of day, how many people are in the room? Write down the two or three readings that produced the most interesting answer, because those are the ones worth reproducing later.

**Challenge: Compare the Label with the Judgement**

The light card already carries a word — **Dark**, **Dim**, **Bright**, **Very Bright** — chosen by a fixed set of thresholds in the code, and the model also receives that word as part of the prompt. Spend a session putting them side by side. Find a light level the card calls **Dim** and see what status the model picks; find one it calls **Bright** and do the same. Sometimes the model simply repeats the label, and sometimes it weighs the temperature and humidity and decides the light is not the main problem at all. Then try the edge cases: sit right on a threshold so the card flickers between two words, and see whether the advice flickers with it. By the end you should be able to say which decisions in this project are made by arithmetic and which are made by the model — and which one you would trust with a room full of people.

4. Troubleshooting
--------------------

**The sensor cards stay at "--.-°C" and the Analyze button never becomes clickable**

* **Cause:** The temperature is still ``null``, so Python is refusing to analyze anything. That happens either in the first two seconds after **Run**, while the sketch is letting the DHT11 settle, or when ``dht.readHumidity()`` and ``dht.readTemperature()`` keep returning ``isnan()`` because the DATA wire is not making contact.
* **Solution:** Give it a few seconds first — the first reading is taken on purpose after a two-second delay. If the cards never fill in, power down and re-seat the **DATA** wire on **D4**, the **5V** wire, and the **GND** wire, then press **Run** again. The Output window prints a ``[SENSOR ERROR]`` line with the reason each time the sketch reports a failure, which tells you the sensor is being reached but not read.

**The light percentage moves the opposite way to the real room**

* **Cause:** The percentage is calculated from the raw voltage on **A0**, and a photoresistor module is a voltage divider — which half of it the photoresistor sits in decides whether more light means a larger or a smaller reading. On a module with the two parts swapped, a brighter room produces a *lower* number, so the card reads **Dark** in daylight.
* **Solution:** Shine a light at the module and watch the card. If the number falls when the room gets brighter, your module is the reversed type — the readings are still perfectly usable, they just run backwards, so trust the percentage you measured rather than the word printed under it. Remember that this value is a relative classroom measurement, not a calibrated brightness in lux, so it is only meaningful compared with other readings from the same sensor in the same place.

**The panel says "Analysis unavailable" instead of an answer**

* **Cause:** ``llm.chat_stream()`` raised an exception, and the code shows the same message for every failure: no key saved yet, a key that was rejected or has run out of credit, or no internet connection on the board.
* **Solution:** Check the board's internet connection first, since the model lives in the cloud. Then confirm your key is still valid and funded in your OpenAI account. The Output window prints an ``[LLM ERROR]`` line with the exception type, which separates a network problem from a rejected key.

**The model's reply comes back as "Mixed" with "The AI response could not be read safely."**

* **Cause:** The answer did not contain usable JSON. This is the parser's fallback, not a crash: the model may have wrapped the object in text, or the stream was cut off before the closing brace arrived. It is rare, because the system prompt asks for JSON only, but a model can still drift.
* **Solution:** Press **Analyze Environment** again — a fresh request usually returns a clean object. If it happens every single time, check that the readings themselves look sane first; a prompt built from ``None`` values would be an odd thing to ask a model to judge.

**The status row sticks on "Analyzing" and never finishes**

* **Cause:** The request was interrupted — the app was stopped, the board was unplugged, or the browser tab lost its socket — so the ``analysis_result`` or ``analysis_error`` message never arrived to clear the spinner.
* **Solution:** Reconnect the USB-C cable if it came loose and press **Run** again, then refresh the Web UI tab. The page asks for the current state as soon as it reconnects, so the sensor cards refill on their own and you can press **Analyze Environment** once more.

5. Summary
-------------

You just gave your board a sense of judgement. The DHT11 and the photoresistor supply three honest numbers, Python turns them into a labelled snapshot, and a cloud model reads that snapshot and tells you what it means for the room you are sitting in — a measurement on one side, an interpretation on the other.

* A **structured answer** is what makes a model usable in a program: ask for named fields like ``status``, ``summary``, and ``suggestion``, and your page can place each one instead of searching through prose
* ``Bridge.notify()`` is the reverse of the Bridge calls you have used before — the sketch starts the conversation twice a second, and Python listens with ``Bridge.provide()``
* The body of the prompt is only three numbers, so every answer is tied to one moment and you can always see exactly what the model was shown
* ``parse_analysis()`` and ``VALID_STATUSES`` are your side of the bargain: strip the fences, pull out the JSON, and replace anything unrecognised with a safe fallback
* Python and the model do different jobs — the code decides what the light *is*, the model decides what it *means* — and neither one is allowed to do the other's work

The next project gives the model ears and a voice: you hold a button and speak into the microphone, speech recognition turns your words into text, the model replies, and the speaker reads that reply out loud so nothing has to appear on a screen at all.
