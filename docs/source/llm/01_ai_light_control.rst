01 AI Light Control
===================

.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

Every project so far has been you giving the orders: a pin number, a slider value, a colour code typed into a Web UI. This project hands the decision to a **large language model** — you type *"turn the light red"*, *"make it blue"*, or *"switch it off"* in plain English, and the model works out what you meant. The RGB LED on your breadboard lights up in the colour the model chose, and nowhere in the project is there a list of the sentences you are allowed to use.

In this lesson, you will learn to:

* Send a sentence from a Web UI to a large language model and get a decision back
* Shape that decision with a **system prompt**, so the reply is always something your code can act on
* Turn the reply into a physical action — a lookup table, a Bridge call, and PWM on three pins
* See where the intelligence actually lives: the model runs in the cloud, while the timing and the hardware stay on the board
* Use the pattern *the model decides, the code enforces* — nothing moves unless the answer is one your program recognises

1. Setup
-----------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_rgb_led` (Common Cathode)
     - 3 * :ref:`cpn_resistor` (220Ω)
     - 1 * USB-C Cable
   * - |list_pan_tilt|
     - |list_rgb_led|
     - |list_220ohm|
     - |list_usb_cable|
   * - 1 * :ref:`cpn_breadboard`
     - Several :ref:`cpn_wires`
     -
     -
   * - |list_breadboard|
     - |list_wire|
     -
     -

**Software Requirements**

This project uses two App Lab **Bricks** — support packages that App Lab adds to your app for you:

* ``web_ui`` — serves the chat page and keeps the browser and Python in sync
* ``cloud_llm`` — sends your message to a cloud language model and streams the answer back

Because the model is reached over the internet, the project needs a key of your own. ``app.yaml`` declares the ``cloud_llm`` brick with an empty ``API_KEY``, so App Lab asks you for an **OpenAI API key** the first time you press **Run** and stores it for you.

The sketch needs no libraries at all — the Bridge library that lets Python call the sketch is part of the UNO Q core, so there is nothing to install.

**Hardware Check**

#. Push the **RGB LED** into the breadboard with each of its four legs in its own column of holes. Three legs are the red, green, and blue anodes; the fourth and longest leg is the **common cathode**.
#. Add the three **220 Ω resistors**, one in series with each anode leg. An LED leg must never reach a pin without its resistor.
#. Run a jumper wire from the common cathode to a **GND** pin on the Robot Shield, then three wires from the far ends of the resistors to **D8**, **D7**, and **D6**.
#. Plug the **USB-C cable** into the UNO Q and your computer, and check that the board powers up.

**Wiring Diagram**

The RGB LED has four legs: the longest one is the **common cathode** and goes to **GND**, while the red, green, and blue anodes go to **D8**, **D7**, and **D6**, each through its own **220 Ω** resistor. Never connect a channel straight to a pin without its resistor — the LED can burn out.

.. image:: /img/wiring/wiring_rgb_led.png
   :width: 500
   :align: center

2. Run the App
----------------

#. Download :download:`01 AI Light Control.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/01.AI.Light.Control.zip>`.
#. Open **Arduino App Lab** and go to **Apps**. Click the dropdown arrow next to **Create new app +** and select **Import App**.

   .. image:: /img/app_import_app.png
      :width: 600

#. Select **Import from Computer**.

   .. image:: /img/app_import_pc.png
      :width: 600

#. Choose the package you downloaded. The app appears in **Apps** — click it to open.
#. With the app open, click the **Run** button (▶) in the top-right corner. The sketch flashes the LED red, then green, then blue as a quick self-test, and the Python side starts the Web UI.

   .. image:: /img/app_run.png
      :width: 500
      :align: center

   .. note::

      The first time you run this project, App Lab asks for your **OpenAI API key**, because the app uses the ``cloud_llm`` brick to reach the model. Paste a key from your OpenAI account and save it — App Lab keeps the key for your board, so you only do this once.

#. The Output window prints *"💬 AI Light Control ready — configure your API Key and start chatting!"* and a **Web UI** tab opens by itself. The status row reads **Connecting** for a moment, then **Connected** with a blue dot.
#. Type a request into the box — the placeholder suggests *"Turn the light red"* — and press **Send** or the Enter key. Your sentence appears in the chat, the model's decision arrives a moment later, and the RGB LED on the breadboard follows it.
#. Keep the conversation going: ask for a few different colours, then ask it to switch the light off. The page looks like this, with the colour the model chose at the top and both halves of the conversation underneath.

   .. image:: img/ai_rgb_result.png
      :width: 600
      :align: center

**How it Works**

Here is the whole path a sentence travels — out of your browser, into the cloud, and back down to three pins.

An App Lab project is a folder of files. Here is what is inside this one:

* ``01 AI Light Control/`` — the app folder

  * ``app.yaml`` — app metadata: name, icon, and the two Bricks the project declares
  * ``README.md`` — a short guide to the project

  * ``python/``

    * ``main.py`` — the chat handler, the cloud model request, the colour lookup, and the Bridge call

  * ``sketch/``

    * ``sketch.ino`` — the RGB LED pins, the colour table, and the Bridge function
    * ``sketch.yaml`` — sketch configuration for the UNO Q board

  * ``assets/``

    * ``index.html`` — the chat page: status row, colour swatch, message list, and input box
    * ``app.js`` — browser logic: sending your sentence, drawing the replies, repainting the swatch
    * ``style.css`` — the visual styling of the page
    * ``libs/socket.io.min.js`` — the Socket.IO client that carries messages between the page and the board
    * ``img/sf_logo.png`` — the logo in the page header
    * ``docs_assets/`` — the result and wiring images used by this documentation

The data path, from a typed sentence to coloured light:

.. mermaid::

   sequenceDiagram
       participant B as Browser (HTML/JS)
       participant P as Python (main.py)
       participant L as Cloud LLM (OpenAI)
       participant S as Sketch (sketch.ino)

       B->>P: socket.emit("command", {text})
       P->>L: CloudLLM.chat_stream(message)
       L-->>P: "blue"
       P->>P: COLOR_CODES lookup - blue becomes 3
       P->>S: Bridge.call("set_color", 3)
       S->>S: setRgb(0, 0, 255) - analogWrite on D8, D7, D6
       P-->>B: socket.emit("response", {text, color})
       B->>B: setColor("blue") - swatch and label

Here is what each piece does:

**Sketch (sketch.ino)** — runs on the STM32 MCU
  * ``setup()`` sets the three pins to outputs and runs a red → green → blue self-test, then calls ``Bridge.begin()``
  * ``setRgb(r, g, b)`` writes the three brightness values with ``analogWrite()`` on **D8** (red), **D7** (green), and **D6** (blue)
  * ``set_color(code)`` is a ``switch`` that turns one integer into a colour: 1 red, 2 green, 3 blue, 4 yellow, 5 white, anything else off
  * ``Bridge.provide("set_color", set_color)`` publishes that function so Python is allowed to call it
  * ``loop()`` only pauses — every colour change arrives as an event

**Python (main.py)** — runs on the Linux MPU
  * ``WebUI()`` starts the server that hands the chat page from ``assets/`` to your browser
  * ``ui.on_message("command", handle_command)`` listens for the sentence the page sends
  * ``CloudLLM(model="openai:gpt-4o-mini", system_prompt=SYSTEM_PROMPT)`` creates the link to the cloud model and fixes its behaviour up front
  * ``llm.chat_stream(message=text)`` sends your words and collects the streamed answer as one word
  * ``COLOR_CODES`` is the lookup table that converts that word into a small integer — and everything that is not in the table is refused
  * ``Bridge.call("set_color", code)`` hands the integer to the sketch
  * ``ui.send_message("response", {...})`` sends the reply text and the colour name back to the page
  * ``App.run()`` starts the app and keeps it alive

**Cloud LLM (behind the ``cloud_llm`` brick)** — runs on OpenAI's servers
  * The **system prompt** lists the five supported colours and the word ``off``, then insists on a one-word answer
  * Your sentence is sent with that instruction over the internet, and the answer comes back as a single word
  * Only this step needs the internet — the page, the sketch, and the LED all run locally

**Bridge** — the channel between the MPU and the MCU
  * Sketch side: ``Bridge.provide("set_color", set_color)`` exposes the colour function
  * Python side: ``Bridge.call("set_color", code)`` invokes it with one integer
  * One small number is the whole protocol — the model never talks to the chip directly

**Browser (HTML/JS)** — runs in your browser
  * ``socket.emit('command', {text})`` sends what you typed; the **Send** button and the Enter key both call ``sendCommand()``
  * ``socket.on('response', ...)`` appends the model's reply to the chat and repaints the colour swatch
  * ``setColor()`` uses a small ``colorHex`` map — ``#ef5350`` red, ``#43a047`` green, ``#1e88e5`` blue, ``#fbc02d`` yellow, ``#fafafa`` white
  * ``socket.on('connect')`` and ``socket.on('disconnect')`` drive the status dot at the top of the card

Notice how little the board has to do with the intelligence. Python does not know what *"something warm and bright"* means — it sends the words somewhere else and waits for one word back. The **system prompt** is what makes that answer usable: it tells the model which words exist, and the code then refuses to move unless the answer is one of them. The model understands the language; your program decides what is safe to do with the answer.

3. Experiment
----------------

**Say It Your Way**

The model reads intent, so you never have to find the one phrase it accepts. Type each request and watch the chat reply and the LED at the same time:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - What you type
     - What happens
   * - *"Turn the light red"*
     - The model answers ``red``; the LED glows red and the swatch is labelled **Red**
   * - *"I want it blue please"*
     - The same colour as any shorter way of asking — the model answers ``blue``
   * - *"Give me something warm and bright"*
     - The model has to choose from the five colours it was told about, and whichever it picks lights up
   * - *"Switch it off"*
     - The model answers ``off``, the sketch writes 0 to all three channels, and the chat replies *"Light turned off"*
   * - *"Make it purple"*
     - ``purple`` is not one of the supported colours, so nothing changes and the chat replies *"I don't know that color. Try: red, green, blue, yellow, white or off."*

**Challenge: Describe a Colour Without Naming It**

Try to change the LED without ever saying one of the five colour words. *"The colour of a ripe tomato."* *"Make it look like the sky at noon."* *"Give me banana."* Some of these descriptions land on a supported colour and the LED obeys; others fall outside and the chat tells you the answer was not recognised. Which descriptions are reliable, and which ones leave the model guessing? Read the chat bubble every time — it always shows you exactly what the model answered, which is the honest record of its decision.

**Challenge: Find the Edges of the System Prompt**

Now try to push the model off its rails. Ask for two colours at once (*"red and green stripes"*). Ask an unrelated question (*"what's the weather like?"*). Try a negation (*"don't turn it red"*). Then ask for a colour that does not exist (*"turn it infra-red"*). For each attempt, notice two things: what the model answered, and how the app reacted when that answer was not in its table. Every miss is a clue about how much freedom the system prompt really leaves the model — and how much your own code still has to police.

4. Troubleshooting
--------------------

**The chat replies "Please configure your API Key."**

* **Cause:** The request to the cloud model failed. The code shows this message for any failure at all: no key saved yet, a key that was rejected or has run out of credit, or no internet connection on the board.
* **Solution:** Check the board's internet connection first, since the model lives in the cloud. Then confirm your key is still valid and funded in your OpenAI account, stop the app, and press **Run** again to enter a fresh key.

**The chat says "Light set to red" but the LED never changes**

* **Cause:** The Bridge call is not reaching the sketch, or the LED circuit is not connected.
* **Solution:** Watch the LED while the app starts — the sketch flashes red, green, and blue before the app is ready, which proves that the wiring and all three channels work. If that self-test stays dark, re-check the wiring; if it flashes but the chat changes nothing, stop the app and run it again so both halves restart together.

**The LED lights the wrong colour**

* **Cause:** The three anode legs are on the wrong pins, so the sketch is driving the wrong channel.
* **Solution:** Follow the wiring diagram again: red to **D8**, green to **D7**, blue to **D6**, each through its own **220 Ω** resistor, with the common cathode (the longest leg) on **GND**. The order of the legs along the LED body does not have to match the order of the pins — what matters is which leg ends up on which pin.

**The Web UI never opens**

* **Cause:** The app is not running yet, or your browser blocked the new tab.
* **Solution:** Click **Run** again and wait for the *"AI Light Control ready"* line in the Output window, then allow pop-ups for App Lab or open the Web UI from the app's tab strip yourself.

**The status dot turns red and reads "Disconnected" while you are chatting**

* **Cause:** The socket between the page and Python dropped — usually because the app stopped or the board was unplugged.
* **Solution:** Reconnect the USB-C cable if it came loose, press **Run** again, and refresh the Web UI tab. The page reconnects on its own once the app is back.

5. Summary
-------------

You just taught your UNO Q to understand you. Instead of writing the exact command for every colour, you described what you wanted in plain English, a cloud model made the decision, and a single small number carried that decision all the way to the LED.

* A **system prompt** is how you turn a chatty model into a reliable one: list the answers you can handle, and ask for nothing else
* Python turns the model's word into an integer with a simple lookup table, and refuses any answer that is not in it
* ``Bridge.call()`` carries that integer across to the sketch, where one ``switch`` and three ``analogWrite()`` calls produce the colour
* The Web UI shows both halves of the exchange — your sentence and the model's decision — so you can always see why the light changed
* The intelligence lives in the cloud, while the board keeps the pins, the timing, and the last word on what is allowed

The next project gives the model more than one job: instead of choosing a colour, it will hold a conversation with you *and* choose an emotion at the same moment, so the board's built-in LED matrix can pull a face while the words appear on screen.
