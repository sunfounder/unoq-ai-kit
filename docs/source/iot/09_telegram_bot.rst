.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

09 Telegram IoT Bot
=====================

In this final lesson of Module C, you'll connect your UNO Q to **Telegram**. You'll create a bot that responds to chat commands — send ``/led_on`` and the LED lights up; send ``/status`` and the bot replies with the current temperature and humidity. Your hardware becomes a chat contact you can message from anywhere.

.. image:: img/telegram_result.png
   :width: 600
   :align: center

In this lesson, you will learn to:

* Create a Telegram Bot with @BotFather and obtain an API token
* Use the **Telegram Bot Brick** to receive messages and send replies
* Register Python command handlers with ``bot.add_command()``
* Read sensors and control hardware via Bridge — triggered by chat messages

1. Build the Circuit
----------------------

**Components Needed**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * :ref:`Arduino Uno Q <cpn_uno_q>`
     - 1 * :ref:`cpn_led` (Red)
     - 1 * :ref:`cpn_resistor` (220Ω)
     - 1 * :ref:`cpn_humiture_sensor`
   * - |list_uno_q|
     - |list_red_led|
     - |list_220ohm|
     - |list_dht11|
   * - 1 * :ref:`cpn_breadboard`
     - Several :ref:`cpn_wires`
     - 1 * USB Cable
     -
   * - |list_breadboard|
     - |list_wire|
     - |list_usb_cable|
     -

**Wiring Diagram**

Connect the DHT11: **VCC** → **3.3V**, **DATA** → **pin 2**, **GND** → **GND**. Connect the LED's anode through a 220Ω resistor to **pin 5**, and its cathode to GND.

.. image:: /img/wiring/wiring_dht11_led.png
   :width: 500
   :align: center

.. note::

   Before running: open Telegram, message **@BotFather**, send ``/newbot``, and follow the prompts. Copy the API token — you'll configure it in the Brick settings.

2. Run the App
----------------


#. In App Lab, go to **Apps** → **Create new app** → **Import App** → **Import from Computer**.

#. Navigate to ``unoq-ai-kit/iot/`` and select ``09 Telegram IoT Bot.zip``. Open it.

#. On the App page, locate the **Telegram Bot** Brick, click **Brick Configuration**, and paste the API token from BotFather.

   .. image:: img/09_telegram_bot_token.png
      :width: 90%

#. Click the **Run** button (▶). Wait for the App to start.

#. Open Telegram, find your bot, and send ``/start`` — it replies with the available commands. Then try:

   * ``/status`` → bot replies with temperature, humidity, and LED state
   * ``/led_on`` → LED turns on, bot: "💡 LED turned ON."
   * ``/led_off`` → LED turns off, bot: "🌙 LED turned OFF."
   * ``/help`` → lists all commands

.. image:: img/telegram_result.png
   :width: 600
   :align: center

**How it Works**

A chat message replaces the browser click — but the pipeline below the surface is the same:

* ``09 Telegram IoT Bot/`` — the app folder

  * Bricks

    * Telegram Bot

  * Files

    * ``python/``

      * ``main.py`` — Bot setup and command handlers

    * ``sketch/``

      * ``sketch.ino`` — DHT11 reading and LED control

    * ``app.yaml`` — App metadata (name, icon, bricks used)

.. mermaid::

   sequenceDiagram
       participant U as Phone (Telegram)
       participant T as Telegram Bot Brick
       participant P as Python (main.py)
       participant S as Sketch (sketch.ino)

       U->>T: User sends "/status"
       T->>P: status_cmd(sender, message)
       P->>S: Bridge.call("get_temperature")
       S-->>P: 25.6
       P->>S: Bridge.call("get_humidity")
       S-->>P: 57.0
       P->>T: sender.reply("🌡 25.6 °C ...")
       T-->>U: Bot message

Here's what each component does:

**Sketch (sketch.ino)** — runs on the STM32 MCU
  * Reads the DHT11 with ``dht.readTemperature()`` and ``dht.readHumidity()``
  * ``Bridge.provide()`` exposes four functions: ``get_temperature``, ``get_humidity``, ``set_led``, and ``get_led_state``
  * Controls the LED on D5 with ``digitalWrite()`` and remembers its state in ``ledState``

**Python (main.py)** — runs on the Linux MPU
  * ``bot = TelegramBot()`` creates the bot using the Telegram Bot Brick
  * ``bot.add_command("status", status_cmd, ...)`` registers each command handler
  * Each handler receives a ``Sender`` and a ``Message`` — replies go out with ``sender.reply(...)``
  * ``/status`` pulls values through ``Bridge.call()``; ``/led_on`` and ``/led_off`` push commands down

**The Telegram Bot Brick** — runs in App Lab
  * Handles the HTTPS connection to Telegram's servers — no manual HTTP requests, no polling code
  * Routes incoming messages to the matching Python command handler
  * The token lives in the Brick configuration, not in the code — safe to share the project

**Error handling that keeps the bot alive**

Every handler wraps its Bridge calls in ``try``/``except`` — if the DHT11 hiccups, the bot replies "❌ I couldn't read the sensor right now. Please try again." instead of crashing the whole App.

3. Experiment
----------------

**Add a Beep Command**

The circuit has an LED — what else could the bot control? Add a passive buzzer on D5's neighbor and a ``/beep`` command. You'll need to:

* Add ``Bridge.provide("beep", ...)`` in the sketch with ``tone()``
* Add a ``beep_cmd`` handler in Python with ``bot.add_command("beep", beep_cmd, ...)``

**Challenge: Personalized Greetings**

``start_cmd`` already uses ``sender.first_name`` in its greeting. Extend ``/status`` to greet the user by name, and make ``/help`` list the commands in your own words.

**Challenge: Threshold Alerts**

Make the bot **proactive**: store the chat ID from the last ``/status`` request, and have the Python app check the temperature in a loop — if it exceeds 30°C, send an unsolicited warning message.

4. Troubleshooting
--------------------

**Bot never responds to messages**

* **Cause:** The token in the Brick configuration is wrong, or the App isn't running.
* **Solution:** Verify the token from @BotFather is pasted exactly. Restart the App and wait for it to fully start before messaging the bot.

**The bot replies but sensor values are wrong or missing**

* **Cause:** The DHT11 is wired incorrectly or needs a moment to stabilize.
* **Solution:** Check VCC → 3.3V, DATA → pin 2, GND → GND. If the bot replies with the error message, wait a few seconds and send ``/status`` again — the DHT11 needs about a second after power-on.

**The bot sees messages but the LED doesn't change**

* **Cause:** The Bridge function name doesn't match between Python and the sketch.
* **Solution:** ``Bridge.call("set_led", True)`` in Python must match ``Bridge.provide("set_led", setLed)`` in the sketch exactly — names are case-sensitive. Open the Monitor for Bridge errors.

**Telegram says "Sorry, this bot is not supported" or the token was leaked**

* **Cause:** The token was exposed (screenshot, shared file) and should be considered compromised.
* **Solution:** Never include a real token in screenshots, documentation, or shared ZIP files. If a token leaks, open @BotFather and revoke/regenerate it — the old one stops working immediately.

5. Summary
-------------

Your hardware is a Telegram contact! In this lesson, you learned:

* How to create a Telegram bot and configure it through the Telegram Bot Brick
* How to register command handlers with ``bot.add_command()`` and reply with ``sender.reply()``
* How to read sensors and control hardware through Bridge — triggered by chat messages
* How to keep a bot resilient with ``try``/``except`` error handling

**Module C complete!** You now have the full IoT toolkit:

* **Local UI** (lessons 01–02): Browser buttons and color pickers → hardware
* **Hardware to browser** (lessons 03–04): Live charts and browser games
* **Cloud** (lessons 05–06): Remote dashboards, gauges, and control
* **Camera and events** (lessons 07–08): Smart doorbell and security monitoring
* **External services** (this lesson): Telegram bots and third-party APIs

In the modules ahead, you'll add the most advanced capability yet — Edge AI vision with the camera, and large language models like Gemini and ChatGPT for AI-driven interaction.
