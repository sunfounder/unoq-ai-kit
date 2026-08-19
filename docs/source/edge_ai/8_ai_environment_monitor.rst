.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

8. Smart Environment Monitor
================================

In this lesson, you'll fuse **sensor data with AI voice output** — the DHT11 reads temperature and humidity, and the UNO Q **speaks the readings aloud** at regular intervals. This is the bridge between the sensor skills from Module A and the AI skills from Module D: your device monitors the environment and reports to you in natural language.

In this lesson, you will learn to:

* Read temperature and humidity from the DHT11 sensor
* Use Text-to-Speech to announce sensor readings on a schedule
* Trigger voice alerts when readings exceed thresholds
* Combine sensor timing (millis) with TTS output

1. Build the Circuit
----------------------

**Components Needed**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * :ref:`Arduino Uno Q <cpn_uno_q>`
     - 1 * Multimedia Carrier
     - 1 * :ref:`cpn_humiture_sensor`
     - Several :ref:`cpn_wires`
   * - |list_uno_q|
     - |list_uno_q|
     - |list_dht11|
     - |list_wire|
   * - 1 * :ref:`cpn_breadboard`
     - 1 * USB Cable
     -
     -
   * - |list_breadboard|
     - |list_usb_cable|
     -
     -

**Wiring Diagram**

.. image:: img/8_env_monitor_fritzing.png
   :width: 700
   :align: center

Here are the connections to make:

#. Connect the DHT11 module: **VCC** → **3.3V**, **DATA** → **digital pin 2**, **GND** → **GND**.

#. The Multimedia Carrier's speaker will announce readings aloud — no extra wiring needed.

2. Code
----------

**Import the Code**

#. In App Lab, go to **Apps** → **Import App** → **Import from Computer**.

#. Navigate to ``unoq-ai-kit/edge_ai/`` and select ``8_ai_environment_monitor.zip``.

#. Open the imported app.

**Run the Code**

#. Click the **Run** button (▶).

#. Every 30 seconds, the speaker announces: "Temperature: 25 degrees Celsius. Humidity: 58 percent."

#. If the temperature exceeds 30°C, the speaker warns: "Warning! High temperature detected."

#. Open the **Monitor** to see the numeric readings alongside the voice announcements.

**The Code**

.. code-block:: cpp
   :linenos:

   /*
    * Lesson 8: Smart Environment Monitor
    * Reads DHT11 sensor and speaks readings via TTS.
    */

   #include <Arduino_RouterBridge.h>
   #include "DHT.h"
   #include "speaker.h"

   #define DHTPIN 2
   #define DHTTYPE DHT11

   DHT dht(DHTPIN, DHTTYPE);

   unsigned long lastAnnounceTime = 0;
   const unsigned long announceInterval = 30000;  // Announce every 30 seconds

   const float tempWarning = 30.0;   // Alert above 30°C
   const float humidWarning = 80.0;  // Alert above 80% humidity

   void announceReadings(float temp, float humidity) {
       char buffer[100];

       // Speak temperature
       sprintf(buffer, "Temperature: %.1f degrees Celsius.", temp);
       Speaker.say(buffer);
       delay(2000);  // Pause between phrases

       // Speak humidity
       sprintf(buffer, "Humidity: %.0f percent.", humidity);
       Speaker.say(buffer);
   }

   void checkWarnings(float temp, float humidity) {
       if (temp > tempWarning) {
           Speaker.say("Warning! High temperature detected.");
           delay(2000);
       }
       if (humidity > humidWarning) {
           Speaker.say("Warning! High humidity detected.");
           delay(2000);
       }
   }

   void setup() {
       Monitor.begin();
       Speaker.begin();
       dht.begin();

       Speaker.say("Environment monitor started.");
   }

   void loop() {
       unsigned long now = millis();

       if (now - lastAnnounceTime >= announceInterval) {
           lastAnnounceTime = now;

           float humidity = dht.readHumidity();
           float temperature = dht.readTemperature();

           if (isnan(humidity) || isnan(temperature)) {
               Monitor.println("Sensor read failed");
               return;
           }

           // Print to Monitor
           Monitor.print("Temp: ");
           Monitor.print(temperature);
           Monitor.print(" °C  Humidity: ");
           Monitor.print(humidity);
           Monitor.println(" %");

           // Speak the readings
           announceReadings(temperature, humidity);

           // Check for warning conditions
           checkWarnings(temperature, humidity);
       }
   }

**How it Works**

.. code-block:: text

   setup() → runs once:
       Initialize DHT11 sensor + speaker
       Announce startup

   loop() → runs forever:
       Has 30 seconds passed since last announcement?
           YES → read DHT11
               Readings valid?
                   YES → print to Monitor
                       Speak temperature + humidity
                       Check warnings (temp > 30°C? humid > 80%?)
       Do nothing until next interval

Here's what's new in this lesson:

* **``sprintf()``** — Formats a string with numbers embedded in it. ``sprintf(buffer, "Temperature: %.1f degrees", temp)`` creates a natural-language sentence from a numeric variable. The ``%.1f`` means "float with 1 decimal place". This is how we convert sensor numbers into speech-friendly text.
* **Scheduled announcements** — ``millis()``-based timing (from Lesson 7) controls when the readings are spoken. The interval should be long enough to not be annoying (30 seconds is a good starting point).
* **Threshold alerts** — The code checks temperature and humidity against warning thresholds after every reading. This is the "smart" in smart monitor — it doesn't just report data, it interprets it and warns when conditions are dangerous.
* **Multi-sensor fusion** — The DHT11 provides two data streams (temperature AND humidity) from one sensor. The code handles both, speaking each with appropriate context.

3. Experiment
----------------

**Adjust the Announcement Interval**

Change ``announceInterval`` to match your use case:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Interval
     - Use Case
   * - ``10000`` (10s)
     - Rapid monitoring (testing or demo)
   * - ``60000`` (1 min)
     - Regular room monitoring
   * - ``300000`` (5 min)
     - Long-term logging, minimal interruption

**Challenge: Multi-Sensor Dashboard**

Add a photoresistor on pin A0 to also measure light level. Speak: "Temperature: 25 degrees. Humidity: 58 percent. Light level: bright."

.. code-block:: cpp

   int lightLevel = analogRead(A0);
   if (lightLevel < 300) {
       Speaker.say("Light level is low.");
   } else if (lightLevel < 700) {
       Speaker.say("Light level is moderate.");
   } else {
       Speaker.say("Light level is bright.");
   }

**Challenge: Voice Query on Demand**

Add a button that triggers an immediate reading announcement when pressed (combine with the microphone from Lesson 6 to make it voice-triggered). This gives the user control over when they hear readings, rather than only on a schedule.

4. Troubleshooting
--------------------

**Speaker announces "Sensor read failed" or values are zero**

* **Cause:** DHT11 wiring issue, or sensor needs time to stabilize.
* **Solution:** Check VCC → 3.3V, DATA → pin 2, GND → GND. Wait 1–2 seconds after power-on for the first valid reading.

**Announcements are too quiet or too loud**

* **Cause:** The Multimedia Carrier's speaker volume setting.
* **Solution:** If your App Lab setup includes volume control, adjust the speaker gain. Otherwise, the volume is fixed at a comfortable room-listening level.

**Speaker cuts off mid-sentence**

* **Cause:** The ``delay()`` after ``Speaker.say()`` is too short for the spoken phrase.
* **Solution:** Increase the delay after longer phrases. As a rule: allow approximately 100ms per word plus 500ms buffer. "Temperature: 25 point 3 degrees Celsius" (~8 words) needs about 1300ms.

**Readings are announced too frequently**

* **Cause:** The ``lastAnnounceTime`` variable isn't being updated correctly.
* **Solution:** Make sure ``lastAnnounceTime = now;`` runs at the start of the ``if`` block, before ``announceReadings()``. If it's missing, the condition is always true and the system announces continuously.

5. Summary
-------------

Your UNO Q now monitors and reports on its environment! In this lesson, you learned:

* How to combine sensor data (DHT11) with AI voice output (TTS)
* How to use ``sprintf()`` to format natural-language messages from numeric data
* How to implement threshold-based alerts that interpret sensor readings
* How to schedule announcements at user-configurable intervals

In the next lesson, you'll step into the role of AI developer — using Edge Impulse to train your own custom model from scratch.
