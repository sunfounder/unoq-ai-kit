.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

6. Home Climate Monitoring System
=====================================

In Lesson 4, you uploaded sensor data to Arduino Cloud. Now you'll build a richer, more responsive **local dashboard** — a web page running directly on the UNO Q that displays real-time temperature, humidity, and light levels with live-updating gauges, a comfort indicator, and a temperature history chart. Anyone on your local network can open it in their browser.

In this lesson, you will learn to:

* Build a multi-widget dashboard with gauges, charts, and status indicators
* Implement comfort zone logic (18–28°C, 30–70% humidity) with visual feedback
* Use a ring buffer in Python to store sensor history for charts
* Drive physical LEDs AND a web dashboard from the same sensor data

1. Build the Circuit
----------------------

**Components Needed**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * :ref:`Arduino Uno Q <cpn_uno_q>`
     - 1 * :ref:`cpn_humiture_sensor`
     - 1 * :ref:`cpn_photoresistor`
     - 1 * :ref:`cpn_resistor` (10kΩ)
   * - |list_uno_q|
     - |list_dht11|
     - |list_photoresistor|
     - |list_10kohm|
   * - 1 * :ref:`cpn_led` (Green)
     - 1 * :ref:`cpn_led` (Red)
     - 2 * :ref:`cpn_resistor` (220Ω)
     - Several :ref:`cpn_wires`
   * - |list_green_led|
     - |list_red_led|
     - |list_220ohm|
     - |list_wire|

**Wiring Diagram**

.. image:: img/6_climate_dashboard_fritzing.png
   :width: 700
   :align: center

#. DHT11: **VCC** → **5V**, **DATA** → **pin 2**, **GND** → **GND**.

#. Photoresistor + 10kΩ voltage divider → **A0**.

#. Green LED (with 220Ω) → **pin 5** (comfort indicator). Red LED (with 220Ω) → **pin 6** (out-of-range indicator).

2. Code
----------

**Import the Code**

#. Go to **My Apps** → **Import App** → **Import from Computer**.

#. Navigate to ``unoq-ai-kit/iot/`` and select ``6_climate_dashboard.zip``. Open it.

**Run the Code**

#. Click **Run** (▶). The dashboard shows a thermometer gauge, humidity gauge, light bar, comfort status text, and a temperature trend chart (last 20 readings).

#. The **green LED** lights when conditions are comfortable (18–28°C, 30–70%). The **red LED** lights when out of range.

.. image:: img/6_climate_dashboard_result.png
   :width: 700
   :align: center

**The Code — sketch.ino**

.. code-block:: cpp
   :linenos:

   #include <Arduino_RouterBridge.h>
   #include "DHT.h"

   #define DHTPIN 2
   #define DHTTYPE DHT11
   DHT dht(DHTPIN, DHTTYPE);

   const int lightPin = A0;
   const int greenLed = 5;
   const int redLed = 6;

   void setup() {
       Monitor.begin();
       dht.begin();
       pinMode(lightPin, INPUT);
       pinMode(greenLed, OUTPUT);
       pinMode(redLed, OUTPUT);

       Bridge.begin();
       Bridge.provide("read_sensors", read_sensors);
       Bridge.provide("set_leds", set_leds);
   }

   void loop() {}

   String read_sensors() {
       float temp = dht.readTemperature();
       float hum = dht.readHumidity();
       int light = analogRead(lightPin);

       if (isnan(temp) || isnan(hum)) return "error";
       return String(temp, 1) + "," + String(hum, 1) + "," + String(light);
   }

   void set_leds(bool comfortable) {
       digitalWrite(greenLed, comfortable ? HIGH : LOW);
       digitalWrite(redLed, comfortable ? LOW : HIGH);
   }

**The Code — main.py**

.. code-block:: python
   :linenos:

   from arduino.app_utils import *
   from arduino.app_bricks.web_ui import WebUI
   from collections import deque
   import time

   ui = WebUI()

   # Comfort thresholds
   TEMP_MIN, TEMP_MAX = 18.0, 28.0
   HUM_MIN, HUM_MAX = 30.0, 70.0

   # Ring buffer for temperature history (last 20 readings)
   temp_history = deque(maxlen=20)

   last_update = 0
   UPDATE_INTERVAL = 2  # seconds

   def is_comfortable(temp, hum):
       return TEMP_MIN <= temp <= TEMP_MAX and HUM_MIN <= hum <= HUM_MAX

   def get_dashboard_data():
       result = Bridge.call("read_sensors")
       if result == "error" or not result:
           return None

       parts = result.split(",")
       temp = float(parts[0])
       hum = float(parts[1])
       light = int(parts[2])
       comfortable = is_comfortable(temp, hum)

       # Update ring buffer
       temp_history.append(temp)

       # Update physical LEDs
       Bridge.call("set_leds", comfortable)

       return {
           "temperature": round(temp, 1),
           "humidity": round(hum, 1),
           "light": light,
           "comfortable": comfortable,
           "comfort_text": "COMFORTABLE" if comfortable else "OUT OF RANGE",
           "history": list(temp_history)
       }

   def on_get_initial_state(client, data):
       dashboard = get_dashboard_data()
       if dashboard:
           ui.send_message('dashboard_update', dashboard, client)

   ui.on_message('get_initial_state', on_get_initial_state)

   # Background: update all clients every 2 seconds
   def broadcast_loop():
       global last_update
       while True:
           now = time.time()
           if now - last_update >= UPDATE_INTERVAL:
               last_update = now
               dashboard = get_dashboard_data()
               if dashboard:
                   ui.send_message('dashboard_update', dashboard)
           time.sleep(0.5)

   import threading
   threading.Thread(target=broadcast_loop, daemon=True).start()

   App.run()

**The Code — app.js (key parts)**

The browser receives dashboard data and updates all widgets:

.. code-block:: javascript

   socket.on('dashboard_update', (data) => {
       // Update gauges
       updateGauge('temp-gauge', data.temperature, 0, 50);
       updateGauge('humid-gauge', data.humidity, 0, 100);
       // Update light bar
       document.getElementById('light-fill').style.width = (data.light/1023*100) + '%';
       // Update comfort indicator
       const indicator = document.getElementById('comfort-indicator');
       indicator.textContent = data.comfort_text;
       indicator.className = data.comfortable ? 'comfortable' : 'warning';
       // Update chart
       drawChart(data.history);
   });

**How it Works**

.. code-block:: text

   Every 2 seconds:
       Sketch: read DHT11 + photoresistor → "25.3,58,612"
       Python: parse → check comfort zone → update ring buffer
               Bridge.call("set_leds", comfortable)  → green or red LED
               ui.send_message('dashboard_update', {...})  → all browsers

   Browser receives:
       { temperature: 25.3, humidity: 58, light: 612,
         comfortable: true, comfort_text: "COMFORTABLE",
         history: [24.8, 24.9, 25.0, 25.1, 25.3, ...] }

Key design elements:

* **Ring buffer** — ``collections.deque(maxlen=20)`` automatically drops old readings. No manual index management needed — Python's standard library handles it.
* **Broadcast to all clients** — ``ui.send_message()`` without a ``client`` argument sends to every connected browser. One UNO Q, many dashboard viewers.
* **Physical + digital feedback** — The same ``comfortable`` boolean drives both the LEDs (hardware) and the dashboard status (software). They stay in sync because both use the same data source.

3. Experiment
----------------

**Customize the Comfort Zone**

Adjust the thresholds at the top of ``main.py``:

.. code-block:: python

   TEMP_MIN, TEMP_MAX = 20.0, 26.0   # Narrower range
   HUM_MIN, HUM_MAX = 40.0, 60.0      # Tighter humidity

**Challenge: Trend Arrows**

In Python, compare ``temp_history[-1]`` (current) to ``temp_history[-2]`` (previous). Add a ``trend`` field: "rising" if current is higher by 0.2°C, "falling" if lower by 0.2°C, "stable" otherwise. Display ↑ ↓ → in the dashboard.

**Challenge: Daily Min/Max**

Track the highest and lowest temperature since startup. Add ``daily_high`` and ``daily_low`` fields to the dashboard data. Display as "Today: 18.5°C – 27.2°C".

4. Troubleshooting
--------------------

**Dashboard shows no data on first load**

* **Cause:** ``get_initial_state`` is received before the first sensor reading.
* **Solution:** The ``on_get_initial_state`` handler reads sensors immediately. If it returns None, the browser shows "Waiting for data..." until the next broadcast.

**History chart is flat for the first minute**

* **Cause:** The ring buffer starts empty and fills over time.
* **Solution:** 20 readings × 2 seconds = 40 seconds to fill the buffer. Until then, the chart shows only the collected points. Add a loading indicator in the UI.

**Green and red LEDs both on or both off**

* **Cause:** ``set_leds()`` logic error, or the pins are swapped.
* **Solution:** Check: green → pin 5, red → pin 6. In ``set_leds()``, the two ``digitalWrite`` calls use opposite conditions — only one LED should be on at a time.

5. Summary
-------------

You've built a professional environmental dashboard! In this lesson, you learned:

* How to broadcast sensor data to multiple browser clients simultaneously
* How to use Python's ``deque`` as a ring buffer for sensor history
* How to implement comfort zone logic that drives both physical LEDs and web UI
* How to structure a dashboard app: background thread for periodic updates, UI handlers for initial state

In the final lesson of this module, you'll connect your UNO Q to Telegram — controlling your hardware through chat messages from anywhere in the world.
