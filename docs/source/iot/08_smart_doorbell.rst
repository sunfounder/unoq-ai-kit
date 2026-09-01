.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

08 Smart Doorbell
=====================

You've built dashboards and remote controls — but all of them waited for a human to look at a screen. Now you'll build a system that **announces events on its own**. Press a button at the "door" and the UNO Q plays a "ding-dong" chime, shows "Someone is at the door!" in the browser, snaps a photo of your visitor, and logs the visit — a complete smart doorbell with camera, sound, and browser notification.

.. image:: img/doorbell_result.png
   :width: 700
   :align: center
   
In this lesson, you will learn to:

* Detect a button press with edge detection and trigger a chain of events
* Play a two-note "ding-dong" chime on a passive buzzer with ``tone()``
* Capture and save visitor photos from the CSI camera
* Combine hardware events, camera snapshots, and browser notifications in one pipeline

1. Build the Circuit
----------------------

**Components Needed**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * :ref:`Arduino Uno Q <cpn_uno_q>`
     - 1 * Multimedia Carrier (with camera)
     - 1 * :ref:`cpn_button`
     - 1 * Passive :ref:`cpn_buzzer`
   * - |list_uno_q|
     - |list_uno_q|
     - |list_button|
     - |list_passive_buzzer|
   * - 1 * :ref:`cpn_breadboard`
     - Several :ref:`cpn_wires`
     - 1 * USB Cable
     -
   * - |list_breadboard|
     - |list_wire|
     - |list_usb_cable|
     -

.. note::

   You used the Multimedia Carrier and camera in Module B — they should already be attached. If not, attach the carrier to the UNO Q and connect the camera's FFC ribbon cable to a CSI connector — the blue side of the cable faces up.

**Wiring Diagram**

Connect the push button between **D2** and **GND** (uses ``INPUT_PULLUP``), and the passive buzzer between **D5** and **GND**.

.. image:: /img/wiring/wiring_pc_buzzer_button.png
   :width: 500
   :align: center

2. Run the App
----------------


#. In App Lab, go to **Apps** → **Create new app** → **Import App** → **Import from Computer**.

#. Navigate to ``unoq-ai-kit/iot/`` and select ``08 Smart Doorbell.zip``. Open it.

#. Click the **Run** button (▶). The Web UI opens with a live camera preview and an empty **Recent Visitors** list.

#. Press the button — the buzzer plays "ding-dong", the page flashes **Someone is at the door!**, a visitor photo is saved, and the event joins the **Recent Visitors** list with its timestamp.

.. image:: img/doorbell_result.png
   :width: 700
   :align: center

**How it Works**

One button press triggers a chain that spans three processors — the MCU plays the chime, the MPU saves a photo, and the browser shows the announcement:

* ``08 Smart Doorbell/`` — the app folder

  * Files

    * ``assets/``

      * ``index.html`` — camera view, announcement banner, visitor list
      * ``app.js`` — Socket.IO events and UI updates
      * ``style.css`` — Visual styling

    * ``python/``

      * ``main.py`` — Camera streaming, photo saving, event relay

    * ``sketch/``

      * ``sketch.ino`` — Button edge detection and doorbell chime

    * ``app.yaml`` — App metadata (name, icon, bricks used)

.. mermaid::

   sequenceDiagram
       participant BT as Button (Hardware)
       participant S as Sketch (sketch.ino)
       participant P as Python (main.py)
       participant B as Browser (HTML/JS)

       BT->>S: Press (HIGH→LOW edge)
       S->>S: playDoorbellChime() — ding-dong
       S-->>P: Bridge.notify("doorbell_pressed")
       P-->>B: doorbell_event {time}
       B->>B: "Someone is at the door!"
       P->>P: save photos/visitor_001.jpg
       P-->>B: visitor_photo {filename, time}

Here's what each component does:

**Sketch (sketch.ino)** — runs on the STM32 MCU
  * Remembers the previous button state and reacts only on the HIGH→LOW transition — holding the button fires exactly one event
  * ``playDoorbellChime()`` plays the two-note chime: ``tone(1047)`` ("ding") for 300 ms, a 150 ms gap, then ``tone(784)`` ("dong") for 500 ms
  * ``Bridge.notify("doorbell_pressed")`` sends the event to Python after the chime starts

**Python (main.py)** — runs on the Linux MPU
  * ``Bridge.provide("doorbell_pressed", doorbell_pressed)`` receives the event
  * Sends the current time to the browser and sets a ``snapshot_requested`` flag
  * The App's ``loop()`` streams the camera preview at about 5 FPS and saves visitor photos as ``photos/visitor_001.jpg``, ``visitor_002.jpg``, and so on
  * ``App.run(user_loop=loop)`` — the custom loop handles camera streaming and deferred snapshot saving

**Browser (HTML/JS)** — runs in the user's browser
  * Shows the live camera preview (JPEG frames from Python)
  * Flashes the **Someone is at the door!** banner on each ``doorbell_event``
  * Displays the latest visitor photo with filename and capture time
  * Keeps the last 10 doorbell events per browser session

**Why save the snapshot in the app loop?**

The camera frame isn't captured inside the Bridge callback — callbacks should be short. Instead, ``doorbell_pressed()`` just sets a flag, and the main loop saves the latest available frame. This keeps Bridge responsive while the camera works at its own pace.

3. Experiment
----------------

**Change the Chime**

The chime is two ``tone()`` calls. Try different note pairs:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Frequencies
     - Effect
   * - 1047 / 784
     - Default — bright "ding-dong" doorbell
   * - 523 / 659
     - Lower, softer chime — like a hotel bell
   * - 1319 / 1047
     - Higher, more urgent — like a phone ring
   * - 1047 / 1047
     - Same note twice — a simple "ding-ding"

**Challenge: Skip Photos at Night**

Currently every press saves a photo. Add a photoresistor on A0 and modify the Python app: if the light level is below a threshold, skip the snapshot and send a "dark" flag to the browser instead. The visitor list should show the event without a photo.

4. Troubleshooting
--------------------

**Pressing the button fires multiple events**

* **Cause:** The edge detection is missing, or the debounce delay is too short.
* **Solution:** The sketch must compare ``lastButtonState == HIGH && buttonState == LOW``. The ``delay(80)`` after each event also absorbs contact bounce — increase it if a single press still registers twice.

**The chime plays but the page doesn't update**

* **Cause:** The Bridge notification name doesn't match, or the Python app stopped.
* **Solution:** Check ``Bridge.notify("doorbell_pressed")`` in the sketch matches ``Bridge.provide("doorbell_pressed", ...)`` in Python exactly. Open the Python Console — you should see "Doorbell pressed at HH:MM:SS".

**No visitor photo is saved**

* **Cause:** The camera is not connected, or the snapshot flag is never consumed.
* **Solution:** Verify the camera FFC cable is seated (blue side up) and the live preview is working. If the preview streams but photos don't save, check that the App runs with ``App.run(user_loop=loop)`` — without the loop, snapshots are never processed.

**The camera preview is choppy or the page is slow**

* **Cause:** The stream interval is too short, or JPEG quality is too high.
* **Solution:** ``STREAM_INTERVAL = 0.20`` (5 FPS) and ``JPEG_QUALITY = 70`` balance quality against network load. Increase the interval to 0.5 for smoother page behavior on slow Wi-Fi.

5. Summary
-------------

You've built a smart doorbell — a button press now announces visitors with sound, photo, and browser notification! In this lesson, you learned:

* How edge detection makes a physical press trigger exactly one event
* How to play a two-note chime with ``tone()`` and timed gaps
* How to stream camera frames to the browser and save snapshots on demand
* How to chain hardware events, camera captures, and browser updates into one pipeline

In the next lesson, you'll turn the doorbell's "event on demand" into a system that watches **continuously** — an IoT security monitor with motion detection, a siren alarm, and automatic snapshots.
