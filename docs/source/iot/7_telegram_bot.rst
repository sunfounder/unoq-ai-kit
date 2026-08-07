.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

7. Telegram Bot Device Control
=================================

In this final lesson of Module B, you'll connect your UNO Q to **Telegram**. You'll create a bot that responds to chat commands — send ``/ledon`` and the LED lights up; send ``/status`` and the bot replies with the current temperature and humidity. Your hardware becomes a chat contact you can message from anywhere.

In this lesson, you will learn to:

* Create a Telegram Bot and obtain an API token
* Poll the Telegram API from Python for new messages
* Parse chat commands and execute hardware actions via Bridge
* Send chat replies with sensor data, status, and emoji

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
   * - 1 * :ref:`cpn_buzzer`
     - Several :ref:`cpn_wires`
     - 1 * :ref:`cpn_breadboard`
     - 1 * USB Cable
   * - |list_active_buzzer|
     - |list_wire|
     - |list_breadboard|
     - |list_usb_cable|

**Wiring Diagram**

.. image:: img/7_telegram_bot_fritzing.png
   :width: 700
   :align: center

#. Red LED (with 220Ω) → **pin 5**. Active buzzer: **VCC** → **pin 6**, **GND** → **GND**. DHT11: **VCC** → **5V**, **DATA** → **pin 2**, **GND** → **GND**.

.. note::

   Before running: open Telegram, message **@BotFather**, send ``/newbot``, and follow the prompts. Copy the API token — you'll configure it in the app settings.

2. Code
----------

**Import the Code**

#. Go to **My Apps** → **Import App** → **Import from Computer**.

#. Navigate to ``unoq-ai-kit/iot/`` and select ``7_telegram_bot.zip``. Open it.

**Run the Code**

#. Click **Run** (▶). The bot connects to Telegram.

#. Open Telegram, find your bot, and send:

   * ``/ledon`` → LED on, bot: "LED is ON 💡"
   * ``/ledoff`` → LED off, bot: "LED is OFF"
   * ``/beep`` → Buzzer sounds, bot: "Beep! 🔊"
   * ``/status`` → Bot replies with temperature, humidity, and LED state
   * ``/help`` → Lists all commands

#. Try from mobile data — the bot responds from anywhere.

.. image:: img/7_telegram_bot_result.png
   :width: 400
   :align: center

**The Code — sketch.ino**

.. code-block:: cpp
   :linenos:

   #include <Arduino_RouterBridge.h>
   #include "DHT.h"

   #define DHTPIN 2
   #define DHTTYPE DHT11
   DHT dht(DHTPIN, DHTTYPE);

   const int ledPin = 5;
   const int buzzerPin = 6;

   void setup() {
       Monitor.begin();
       dht.begin();
       pinMode(ledPin, OUTPUT);
       pinMode(buzzerPin, OUTPUT);

       Bridge.begin();
       Bridge.provide("set_led", set_led);
       Bridge.provide("beep", beep);
       Bridge.provide("read_sensors", read_sensors);
   }

   void loop() {}

   void set_led(bool state) {
       digitalWrite(ledPin, state ? HIGH : LOW);
   }

   void beep(int duration) {
       digitalWrite(buzzerPin, HIGH);
       delay(duration);
       digitalWrite(buzzerPin, LOW);
   }

   String read_sensors() {
       float temp = dht.readTemperature();
       float hum = dht.readHumidity();
       if (isnan(temp) || isnan(hum)) return "error";
       return String(temp, 1) + "," + String(hum, 1);
   }

**The Code — main.py**

.. code-block:: python
   :linenos:

   from arduino.app_utils import *
   import requests
   import time

   # Configure via environment variable or hard-code for testing
   BOT_TOKEN = App.get_setting("TELEGRAM_BOT_TOKEN", "")
   API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

   last_update_id = 0

   def get_updates():
       global last_update_id
       try:
           resp = requests.get(f"{API_URL}/getUpdates",
               params={"offset": last_update_id + 1, "timeout": 10})
           if resp.status_code == 200:
               data = resp.json()
               if data["ok"] and data["result"]:
                   for update in data["result"]:
                       last_update_id = update["update_id"]
                       msg = update.get("message", {})
                       chat_id = msg.get("chat", {}).get("id")
                       text = msg.get("text", "").lower()
                       if chat_id and text:
                           process_command(chat_id, text)
       except Exception as e:
           print(f"Telegram error: {e}")

   def send_message(chat_id, text):
       try:
           requests.post(f"{API_URL}/sendMessage",
               json={"chat_id": chat_id, "text": text})
       except Exception as e:
           print(f"Send error: {e}")

   def process_command(chat_id, command):
       if command == "/ledon":
           Bridge.call("set_led", True)
           send_message(chat_id, "LED is ON \U0001F4A1")

       elif command == "/ledoff":
           Bridge.call("set_led", False)
           send_message(chat_id, "LED is OFF")

       elif command == "/beep":
           Bridge.call("beep", 200)
           send_message(chat_id, "Beep! \U0001F50A")

       elif command == "/status":
           result = Bridge.call("read_sensors")
           if result == "error" or not result:
               send_message(chat_id, "Sensor read failed. Try again.")
               return
           parts = result.split(",")
           reply = (f"\U0001F321 Temperature: {parts[0]} °C\n"
                    f"\U0001F4A7 Humidity: {parts[1]} %")
           send_message(chat_id, reply)

       elif command == "/help":
           send_message(chat_id,
               "Available commands:\n"
               "/ledon — Turn LED on\n"
               "/ledoff — Turn LED off\n"
               "/beep — Sound the buzzer\n"
               "/status — Get sensor readings\n"
               "/help — Show this message")

       else:
           send_message(chat_id, "Unknown command. Type /help for a list.")

   # Main loop: poll Telegram every 2 seconds
   def poll_loop():
       while True:
           get_updates()
           time.sleep(2)

   import threading
   threading.Thread(target=poll_loop, daemon=True).start()

   print("Telegram bot started")
   App.run()

**How it Works**

.. mermaid::

   sequenceDiagram
       participant U as Phone (Telegram)
       participant T as Telegram API
       participant P as Python (main.py)
       participant S as Sketch (sketch.ino)

       U->>T: User sends "/ledon"
       loop every 2s
           P->>T: get_updates()
           T-->>P: "/ledon", chat_id=12345
       end
       P->>S: Bridge.call("set_led", True)
       S->>S: digitalWrite(5, HIGH)
       P->>T: sendMessage("LED is ON")
       T-->>U: "LED is ON 💡"

The architecture adds an **external API** to the familiar pattern. Instead of a browser or cloud dashboard triggering events, Python polls the Telegram API over HTTPS. When it finds a new message, it parses the command and calls the sketch via Bridge — the same Bridge pattern used in every lesson.

Key design choices:

* **Polling, not webhooks** — ``requests.get("/getUpdates")`` every 2 seconds. Webhooks would be more efficient, but polling is simpler and more reliable on variable network connections. The ``offset`` parameter ensures each message is processed only once.
* **Command parsing in Python** — The ``if / elif`` chain routes each ``/command`` to its handler. ``.lower()`` normalizes input. Unknown commands get a helpful ``/help`` reply instead of silence.
* **Emoji via Unicode escapes** — ``\U0001F4A1`` = 💡, ``\U0001F50A`` = 🔊, ``\U0001F321`` = 🌡. These work in any Telegram client.

3. Experiment
----------------

**Add a Photo Command**

If your camera is connected, add a ``/photo`` command. In the sketch, expose ``capture_image()`` that returns a base64-encoded JPEG. In Python, use ``requests.post(f"{API_URL}/sendPhoto", ...)`` with the image data.

**Challenge: Scheduled Alerts**

Instead of only responding to commands, make the bot **proactive**: if temperature exceeds 30°C, send an alert to a pre-configured chat ID without waiting for a ``/status`` request.

**Challenge: Multi-User Access Control**

Store authorized Telegram user IDs. Only respond to commands from known users; reply "Access denied" to unknown ones. Add ``/authorize <password>`` to let new users register.

4. Troubleshooting
--------------------

**Bot never responds to messages**

* **Cause:** The bot token is wrong, ``get_updates()`` isn't running, or the UNO Q has no internet access.
* **Solution:** Verify the token from @BotFather. Add ``print()`` in ``get_updates()`` to see HTTP responses. Check that the UNO Q's Wi-Fi has internet access (not just local network).

**getUpdates returns old messages repeatedly**

* **Cause:** ``last_update_id`` isn't being updated correctly.
* **Solution:** The ``offset = last_update_id + 1`` parameter tells Telegram to skip already-processed messages. Make sure ``last_update_id = update["update_id"]`` runs for every received update.

**Telegram rate limits — bot stops responding after heavy testing**

* **Cause:** Telegram limits bots to ~30 messages/second. Aggressive testing can hit this.
* **Solution:** The 2-second poll interval keeps you well within limits. If rate-limited, wait 30 seconds and try again — limits reset quickly.

**Bot works on Wi-Fi but not on mobile data**

* **Cause:** The bot connects to Telegram's cloud API (outbound HTTPS), so it should work from any network. If it doesn't, check your UNO Q's DNS or firewall settings.

5. Summary
-------------

Your hardware is a Telegram contact! In this lesson, you learned:

* How to poll the Telegram Bot API with Python's ``requests`` library
* How to parse chat commands and execute hardware actions via Bridge
* How to send formatted replies with sensor data, help text, and emoji
* How to integrate an external internet API into the Python → Bridge → Sketch pipeline

**Module B complete!** You now have the full IoT toolkit:

* **Local UI** (Lessons 1–2): Browser buttons and sliders → hardware
* **Cloud** (Lessons 3–4): Remote dashboards, gauges, and charts
* **Games** (Lesson 5): Physical inputs → browser-based experiences
* **Dashboards** (Lesson 6): Multi-widget displays with broadcast
* **External APIs** (Lesson 7): Telegram bots and third-party services

In Module C, you'll add the most advanced capability yet — connecting your UNO Q to large language models like Gemini and ChatGPT for AI-driven interaction.
