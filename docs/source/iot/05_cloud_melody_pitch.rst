.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

05 Arduino Cloud Melody Pitch
===================================

So far, your web controls worked over a local connection — your browser and UNO Q were on the same network. Now you'll use **Arduino Cloud** to control your hardware from **anywhere with internet access**. A cloud slider lets you raise or lower the pitch of a repeating four-note melody (C4 → E4 → G4 → C5) — move the slider on your phone and the melody shifts in real time.

   .. image:: img/3_cloud_dashboard_slider.png
      :width: 90%

In this lesson, you will learn to:

* Connect your UNO Q to Arduino Cloud
* Sync cloud variables between a web dashboard and your Python code
* Use a cloud slider to control a passive buzzer's pitch
* Understand the cloud → Python → Bridge → sketch → hardware pipeline

1. Build the Circuit
----------------------

**Components Needed**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * :ref:`Arduino Uno Q <cpn_uno_q>`
     - 1 * Passive :ref:`cpn_buzzer`
     - Several :ref:`cpn_wires`
     - 1 * USB Cable
   * - |list_uno_q|
     - |list_passive_buzzer|
     - |list_wire|
     - |list_usb_cable|


**Wiring Diagram**

Connect the passive buzzer between **D5** and **GND** — the sketch drives it with ``tone()``.

.. image:: /img/wiring/wiring_pc_buzzer.png
   :width: 500
   :align: center

2. Setup
---------------

**1. Create a Device**

#. Navigate to the |link_arduino_cloud| page and log in or create an account.

#. Go to the |link_cloud_devices| page and create a device.

   .. image:: img/3_cloud_new_device.png
      :width: 90%

#. Select **Arduino UNO Q** under **Manual Setup**. 

   .. image:: img/3_cloud_device_q.png
      :width: 90%

#. Follow the on-screen instructions, enter a **Device Name**, then click **Continue**.

   .. note:: 

      We recommend clicking **Download** to save the generated **Device ID** and **Secret Key**, as you will need them later when configuring the Arduino Cloud Brick.

   .. image:: img/3_cloud_device_id.png
      :width: 90%

**2. Create a Thing**

#. Go to the |link_cloud_things| page and create a new thing. Name it "Buzzer Pitch Control".

   .. image:: img/3_cloud_new_thing.png
      :width: 90%

#. Inside the thing, create a new **Integer** variable and name it "pitch".

   .. image:: img/3_cloud_thing_integer.png
      :width: 90%

#. Associate the device you created with this thing:

   * Inside the thing, select **Associated Device**.

    .. image:: img/3_cloud_thing_associated.png
       

   * Click **Choose from your list**

     .. image:: img/3_cloud_thing_choose.png
     

   * Select the device you created and click **CONFIRM**

     .. image:: img/3_cloud_thing_device.png


**3. Create a Dashboard**

#. Navigate to the |link_cloud_dashboards| page and create a dashboard named "Buzzer Control".

   .. image:: img/3_cloud_dashboard_new.png
      :width: 90%

#. Inside the dashboard, click on **Edit**.

   .. image:: img/3_cloud_dashboard_edit.png
      :width: 90%

#. Select the **Thing** tab and select the Thing you just created.

   .. image:: img/3_cloud_dashboard_thing.png
      :width: 90%

#. This will automatically assign a slider widget to the ``pitch`` variable. Click **DONE**.

   .. image:: img/3_cloud_dashboard_slider.png
      :width: 90%

3. Run the App
----------------

#. In App Lab, go to **Apps** → **Import App** → **Import from Computer**.

#. Navigate to ``unoq-ai-kit/iot/`` and select ``05 Arduino Cloud Melody Pitch.zip``. Open it.

#. Click on the "Arduino Cloud" Brick, then click the "Brick Configuration" button.

   .. image:: img/03_cloud_brick_configure.png
      :width: 90%

#. Enter the **Device ID** and **Secret Key** you saved when creating the device.

   .. image:: img/3_cloud_brick_secret_id.png
      :width: 90%
      
#. Click the **Run** button (▶). The melody plays immediately at the default pitch. Open the cloud dashboard on your phone — move the slider and the melody pitch shifts in real time.

   .. image:: img/4_cloud_result.png
      :width: 90%

**How it Works**

The cloud melody project is a multi-file app — the sketch plays the melody on the MCU, and Python handles the cloud connection:

* ``05 Arduino Cloud Melody Pitch/`` — the app folder

  * Bricks

    * Arduino Cloud

  * Files

    * ``python/``

      * ``main.py`` — Cloud variable registration and callback

    * ``sketch/``

      * ``sketch.ino`` — Melody playback on D5

    * ``app.yaml`` — App metadata (name, icon, bricks used)

.. mermaid::

   sequenceDiagram
       participant C as Phone (Cloud Dashboard)
       participant A as Arduino Cloud
       participant P as Python (main.py)
       participant S as Sketch (sketch.ino)

       C->>A: Move slider → pitch = 40
       A->>P: pitch_callback(client, 40)
       P->>S: Bridge.call("set_pitch_level", 40)
       S->>S: pitchLevel = 40 → melody plays higher

Here's what each component does:

**Sketch (sketch.ino)** — runs on the STM32 MCU
  * Plays a four-note melody — C4, E4, G4, C5 — continuously, using ``tone()`` to generate each frequency on D5
  * Times each 250 ms note with ``millis()`` instead of ``delay()``, so cloud updates arrive between notes
  * ``setPitchLevel()`` constrains the incoming value (0–50) and maps it to a pitch percentage (50%–200%) that shifts the whole melody
  * ``Bridge.provide("set_pitch_level", setPitchLevel)`` exposes the update function to Python

**Python (main.py)** — runs on the Linux MPU
  * ``iot_cloud.register("pitch", value=25, on_write=pitch_callback)`` registers the cloud variable with a default of 25
  * ``pitch_callback()`` fires on every slider change — it clamps the value and calls ``Bridge.call("set_pitch_level", pitch_level)``
  * The melody keeps playing regardless — the cloud only changes the pitch

4. Experiment
----------------

**Adjust the Pitch Range**

Change ``MIN_PITCH_PERCENT`` and ``MAX_PITCH_PERCENT`` in the sketch to control how far the cloud slider shifts the pitch. Try 80 to 120 for a subtle effect, or 25 to 400 for extreme range.

**Challenge: Add More Notes**

Add a fifth note to the ``MELODY`` array — try inserting G4 (392 Hz) between the existing notes so the melody goes C4→E4→G4→G4→C5. The ``MELODY_LENGTH`` calculation adapts automatically.

5. Troubleshooting
--------------------

**Cloud dashboard shows "Device Offline"**

* **Cause:** The UNO Q isn't connected to Wi-Fi, or cloud credentials are wrong.
* **Solution:** Check Wi-Fi connection. Re-enter the cloud device credentials in App Lab's settings.

**Cloud slider moves but melody pitch doesn't change**

* **Cause:** ``Bridge.call()`` isn't reaching the sketch, or the variable name doesn't match.
* **Solution:** Check that the sketch's ``Bridge.provide("set_pitch_level", ...)`` name matches Python's ``Bridge.call("set_pitch_level", ...)`` exactly.

**Buzzer just clicks instead of playing tones**

* **Cause:** Using an active buzzer (fixed pitch) instead of a passive one.
* **Solution:** Make sure you're using the passive buzzer. Active buzzers can't play variable frequencies — they only do on/off at a single frequency.

6. Summary
-------------

Your hardware is now internet-controlled! In this lesson, you learned:

* How to use the ``ArduinoCloud`` brick to sync variables between cloud and device
* How ``cloud.register(on_write=...)`` triggers Python when dashboard values change
* How ``millis()``-based timing drives a melody loop without blocking
* That the Bridge pattern stays the same whether the trigger is local (browser) or remote (cloud)

In the next lesson, you'll reverse the data flow — uploading sensor readings from your UNO Q to the cloud for live visualization.
