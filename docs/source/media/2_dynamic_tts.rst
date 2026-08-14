.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

02 Dynamic TTS
=================

In Lesson 1, you made the speaker say a fixed sentence. Now you'll make it speak **dynamic content** — sensor readings that change in real time. A DHT11 sensor measures temperature and humidity, and the speaker announces the values aloud every 30 seconds, like a talking weather station.

In this lesson, you will learn to:

* Read sensor data from the DHT11 via Bridge
* Format dynamic values into speech using Python f-strings
* Announce sensor readings on a repeating interval

1. Setup
----------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_dht11_module`
     - 1 * USB Cable
     - Several :ref:`cpn_wires`
   * - |list_pan_tilt|
     - |list_dht11|
     - |list_usb_cable|
     - |list_wire|

.. note::

   The DHT11 module connects to the Robotshield. The sensor is read by the sketch and the data is sent to Python through Bridge.

**Software Requirements**

This project uses the following App Lab Bricks and libraries:

* Bricks: 

  * ``robot_shield`` (Robot Shield hardware access)
  * ``sunfounder_tts`` (EdgeTTS engine)

* Libraries:

  * ``DHT sensor library`` (reads temperature and humidity from DHT11/DHT22 sensors)
  * ``Adafruit Unified Sensor`` (common interface for Adafruit sensor libraries) 

**Wiring Diagram**

Connect the DHT11: VCC to 3.3V, DATA to pin 2, GND to GND.

.. image:: /img/wiring/wiring_dht11.png
   :width: 500
   :align: center

2. Code
----------

**Import and Run the Code**

All code for this course is provided as ``.zip`` files that you can import directly into App Lab.

#. Open **Arduino App Lab**, import ``02 Dynamic TTS Weather Reporter.zip`` from ``unoq-ai-kit/media/``.

#. Click **Run** (▶). Every 30 seconds, the speaker announces:

   *"The temperature is 26.3 degrees Celsius. The humidity is 58.2 percent."*

#. Breathe warm air onto the DHT11 — the temperature rises, and the next announcement reflects the change.

**The Code**

.. code-block:: python
   :linenos:

   import time
   from arduino.app_utils import Bridge
   from sunfounder_tts import EdgeTTS

   WEATHER_RPC = "read_weather"
   ANNOUNCEMENT_INTERVAL = 30

   tts = EdgeTTS(gain=0.4)
   tts.set_voice("en-US-JennyNeural")

   while True:
       sensor_data = str(Bridge.call(WEATHER_RPC, "")).strip()

       temperature_text, humidity_text = sensor_data.split(",", 1)
       temperature = float(temperature_text)
       humidity = float(humidity_text)

       message = (
           f"The temperature is {temperature:.1f} degrees Celsius. "
           f"The humidity is {humidity:.1f} percent."
       )

       tts.say(message)
       time.sleep(ANNOUNCEMENT_INTERVAL)

**How it Works**

This is your first lesson where the Python code and the sketch work together. They run on two different processors and communicate through **Bridge**:

.. mermaid::

   sequenceDiagram
       participant S as Sketch (sketch.ino)
       participant P as Python (main.py)

       loop every 30s
           P->>S: Bridge.call("read_weather")
           S->>S: dht.readTemperature()
           S->>S: dht.readHumidity()
           S-->>P: "26.3,58.2"
           P->>P: split string → temp, hum
           P->>P: f-string formats sentence
           P->>P: tts.say(message)
       end

**Sketch (sketch.ino)** — runs on the STM32 MCU

The sketch reads the DHT11 sensor and registers an RPC function via Bridge:

.. code-block:: cpp

   Bridge.provide("read_weather", readWeather);

   String readWeather(String message) {
       float temperature = dht.readTemperature();
       float humidity = dht.readHumidity();
       return String(temperature, 1) + "," + String(humidity, 1);
   }

* ``Bridge.provide("read_weather", readWeather)`` — Registers a function that Python can call remotely. The sketch doesn't call it itself — it waits for Python to request it.
* The function reads temperature and humidity, then returns them as a comma-separated string like ``"26.3,58.2"``. This simple format is easy for Python to parse.

**Python (main.py)** — runs on the Linux MPU

Python calls the sketch every 30 seconds, formats the result, and speaks:

.. code-block:: python

   sensor_data = str(Bridge.call("read_weather", "")).strip()

   temperature_text, humidity_text = sensor_data.split(",", 1)
   temperature = float(temperature_text)
   humidity = float(humidity_text)

   message = f"The temperature is {temperature:.1f} degrees Celsius. "
   message += f"The humidity is {humidity:.1f} percent."

   tts.say(message)

* ``Bridge.call("read_weather", "")`` — Calls the sketch's registered function and gets back a result. This is the key line that connects Python to the sketch.
* ``.split(",", 1)`` — Breaks ``"26.3,58.2"`` into ``["26.3", "58.2"]``.
* An **f-string** inserts the live numbers into a readable sentence. Because the readings change, the sentence changes — this is the core concept: **changing data → changing speech**.

3. Experiment
----------------

**Change the Interval**

``ANNOUNCEMENT_INTERVAL = 30`` controls how often the speaker talks:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Value
     - Effect
   * - 10
     - Every 10 seconds — good for testing
   * - 30
     - Default — once per half minute
   * - 60
     - Once per minute — like a real weather station

**Challenge: Customize the Message**

Change the f-string to make the announcement sound different:

.. code-block:: python

   # Casual
   message = f"It's {temperature:.0f}°C and {humidity:.0f}% humidity."

   # Formal
   message = f"Current conditions: {temperature:.1f}°C, {humidity:.1f}% RH."

4. Troubleshooting
--------------------

**"Failed to read from the DHT11 sensor"**

* **Cause:** The DHT11 is wired incorrectly, or the library is missing.
* **Solution:** Check connections: VCC→3.3V, DATA→D2, GND→GND. Install the DHT sensor library if prompted.

**No sound from the speaker**

* **Cause:** The audio environment isn't configured.
* **Solution:** Run ``./docker-img-make`` in the terminal. Verify Lesson 01 works on the same hardware.

5. Summary
-------------

You've built a talking weather station. In this lesson, you learned:

* How Bridge passes sensor data from sketch to Python
* How f-strings format numbers into natural speech
* How to create a repeating announcement loop

In the next lesson, the direction reverses — instead of the board speaking to you, you'll speak to the board.
