.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

4. Environmental Monitoring System
======================================

In the previous lesson, commands flowed **from** the cloud **to** your device. Now you'll reverse the flow — uploading temperature, humidity, and light data **from** your UNO Q **up to** Arduino Cloud, where you can view it as live charts and gauges. This is the core pattern of IoT: devices report, cloud stores and visualizes.

In this lesson, you will learn to:

* Read multiple sensors (DHT11 + photoresistor) and upload data to the cloud
* Create cloud dashboards with gauges, charts, and numeric widgets
* Schedule periodic uploads from Python using non-blocking timing
* Handle sensor read failures gracefully in a cloud-connected app

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
   * - Several :ref:`cpn_wires`
     - 1 * :ref:`cpn_breadboard`
     - 1 * USB Cable
     -
   * - |list_wire|
     - |list_breadboard|
     - |list_usb_cable|
     -

**Wiring Diagram**

.. image:: img/4_cloud_env_fritzing.png
   :width: 700
   :align: center

#. DHT11: **VCC** → **5V**, **DATA** → **pin 2**, **GND** → **GND**.

#. Photoresistor voltage divider: one leg → **5V**, other leg → **A0** AND through 10kΩ → **GND**.

2. Code
----------

**1. 创建设备**

#. Navigate to the [Arduino Cloud](https://app.arduino.cc/) page and log in / create an account.

#. Go to the [devices](https://app.arduino.cc/devices) page and create a device

   .. image:: img/3_iot_new_device.png

#. selecting the Arduino UNO Q under "manual setup". Follow the instructions and take note of the device_id and secret_key provided in the setup.

   .. note::

      这里建议点击DOWNLOAD来保存生成的device_id and secret_key。

   .. image:: img/3_iot_device_id.png

**2. 创建things**

#. Go to the [things](https://app.arduino.cc/things) page and create a new thing, 将它命名为“Environment Monitor”。

   .. image:: img/3_iot_new_thing.png

#. Inside the thing, create a new **Floating Point Number** variable, and name it "temperature". 

   .. image:: img/4_cloud_thing_envirn.png

#. 使用同样的方法再创建以下两个变量。

   * ``humidity``      Floating Point Number
   * ``led``           Boolean   

   .. image:: img/4_cloud_humidity_led.png


#. We also need to associate the device we created with this thing


   * Inside the thing，选择Associated Device.

    .. image:: img/4_cloud_thing_associated.png

   * 点击 Choose from your list

     .. image:: img/4_cloud_thing_choose.png

   * 选择你刚才创建的设备，并点击CONFIRM

     .. image:: img/4_cloud_thing_device.png 

**3. 创建dashboards**

#. Finally, navigate to the dashboards页面： https://app.arduino.cc/dashboards, and create a dashboard，叫做“Environment Dashboard”。

   .. image:: img/3_iot_dashboard_new.png 

#. Inside the dashboard, click on "Edit", 

   .. image:: img/4_cloud_dashboard_edit.png

#. and select the Thing tab, and select the Thing we just created。

   * 将temperature and humidity的widgets设为value
   * 将led的widget设为 switch
   * 最后点击**CREATE WIDGETS**.

   .. image:: img/4_cloud_dashboard_thing.png

#. 现在来设置widget的名字和范围等。选择一个控件，然后点击**Open settings**。

   .. image:: img/4_cloud_widget_setting.png

#. 在设置页面，写上widget的名字，以及其他设置。


   .. image:: img/4_cloud_widget_set_name.png


#. 现在你可以在Dashboard上看到设置好的3个widget，可以点击DONE。

   .. image:: img/4_cloud_dashboard_finish.png


**4. Import the Code**

#. In App Lab, go to **My Apps** → **Import App** → **Import from Computer**.

#. Navigate to ``unoq-ai-kit/iot/`` and select ``04 Arduino Cloud Environment Monitor.zip``. Open it.

#. click on the "Arduino Cloud" Brick, then click on the "Brick Configuration" button.

   .. image:: img/03_iot_brick_configure.png

**5. Run the Code**

#. Click the **Run** button (▶).






**Import the Code**

#. Go to **My Apps** → **Import App** → **Import from Computer**.

#. Navigate to ``unoq-ai-kit/iot/`` and select ``4_cloud_environment.zip``. Open it.

**Run the Code**

#. Click **Run** (▶). Open the Arduino Cloud Dashboard. You'll see a **temperature gauge**, **humidity gauge**, and a **chart** plotting temperature over time.

#. Breathe on the DHT11 — watch the humidity gauge rise. Shine a light on the photoresistor — watch the light level jump.

.. image:: img/4_cloud_env_result.png
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

   void setup() {
       Monitor.begin();
       dht.begin();
       pinMode(lightPin, INPUT);

       Bridge.begin();
       Bridge.provide("read_sensors", read_sensors);
   }

   void loop() {}

   String read_sensors() {
       float temp = dht.readTemperature();
       float hum = dht.readHumidity();
       int light = analogRead(lightPin);

       if (isnan(temp) || isnan(hum)) {
           return "error";
       }

       // Return as comma-separated string
       return String(temp, 1) + "," + String(hum, 1) + "," + String(light);
   }

**The Code — main.py**

.. code-block:: python
   :linenos:

   from arduino.app_utils import *
   from arduino.app_bricks.arduino_cloud import ArduinoCloud
   import time

   cloud = ArduinoCloud()

   # Register cloud variables
   temp_var = cloud.add_variable("temperature", 0.0)
   hum_var = cloud.add_variable("humidity", 0.0)
   light_var = cloud.add_variable("light_level", 0)

   last_upload = 0
   UPLOAD_INTERVAL = 10  # seconds

   def upload_readings():
       result = Bridge.call("read_sensors")

       if result == "error" or not result:
           print("Sensor read failed")
           return

       parts = result.split(",")
       temp = float(parts[0])
       hum = float(parts[1])
       light = int(parts[2])

       cloud.update(temp_var, temp)
       cloud.update(hum_var, hum)
       cloud.update(light_var, light)

       print(f"Uploaded: {temp}°C, {hum}%, light={light}")

   def on_get_initial_state(client, data):
       ui.send_message('status', {
           "temp": cloud.get(temp_var),
           "hum": cloud.get(hum_var),
           "light": cloud.get(light_var)
       }, client)

   ui = WebUI()
   ui.on_message('get_initial_state', on_get_initial_state)

   # Main loop: upload periodically
   while True:
       now = time.time()
       if now - last_upload >= UPLOAD_INTERVAL:
           last_upload = now
           upload_readings()
       time.sleep(1)

   App.run()

**How it Works**

.. mermaid::

   sequenceDiagram
       participant S as Sketch (sketch.ino)
       participant P as Python (main.py)
       participant C as Arduino Cloud

       loop every 10s
           S->>S: read_sensors()
           S-->>P: "25.3,58,612"
           P->>P: split string -> temp, hum, light
           P->>C: cloud.update(temp_var, 25.3)
           P->>C: cloud.update(hum_var, 58)
           P->>C: cloud.update(light_var, 612)
           C->>C: Dashboard gauges update
       end

The data flow is now **device → cloud**: the sketch reads sensors, Python polls periodically, and ``cloud.update()`` pushes values to Arduino Cloud. The cloud dashboard reads these variables and updates gauges and charts automatically — no extra code needed for visualization.

.. note::

   The sketch returns sensor data as a **comma-separated string** because ``Bridge.provide()`` returns a single value. This is a practical pattern — pack multiple readings into one string, then unpack in Python with ``split(",")``. For more complex data, you could use JSON.

3. Experiment
----------------

**Adjust the Upload Interval**

Change ``UPLOAD_INTERVAL``: 5 seconds for rapid demos, 30 seconds for room monitoring, 300 seconds for long-term logging.

**Challenge: Add Alert Thresholds**

In Python, check if temperature > 30°C after each reading. If so, update a ``cloud.add_variable("alert", "")`` with a warning message — the dashboard shows a red warning banner.

**Challenge: Local + Cloud Dashboard**

Add a Web UI alongside the cloud dashboard. The local browser shows instant readings (fast, no cloud latency); the cloud dashboard shows history (accessible from anywhere). Use both ``WebUI`` and ``ArduinoCloud`` bricks in the same app.

4. Troubleshooting
--------------------

**Dashboard shows stale or no data**

* **Cause:** ``cloud.update()`` isn't being called, or Wi-Fi is disconnected.
* **Solution:** Add ``print()`` in ``upload_readings()`` to verify it runs. Check Wi-Fi connection. The Arduino Cloud brick handles reconnection automatically.

**Sensor reads always return "error"**

* **Cause:** DHT11 wiring issue or the sensor needs time to stabilize.
* **Solution:** Check VCC → 5V, DATA → pin 2, GND → GND. Wait 1–2 seconds after power-on for the first valid reading.

**Light level stuck at 0 or 1023**

* **Cause:** Voltage divider wiring error, or resistor value mismatch.
* **Solution:** Photoresistor leg 1 → 5V, leg 2 → A0 AND through 10kΩ → GND. Bright light = low photoresistor resistance = high ADC reading.

5. Summary
-------------

Your UNO Q is a cloud-connected sensor station! In this lesson, you learned:

* How to upload sensor data from sketch → Python → Arduino Cloud
* How to pack multiple readings into a comma-separated string for Bridge transport
* How to schedule periodic uploads with Python's ``time.time()``
* How to create cloud dashboards without writing visualization code

In the next lesson, you'll build something fun — a browser game controlled by a physical button.
