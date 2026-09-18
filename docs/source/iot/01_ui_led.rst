.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

01 UI Control LED
=====================

In Module A, you controlled an LED with code running on the UNO Q. In Module B, you used the Multimedia Carrier's built-in speaker, microphone, and camera. Now you'll control hardware from a **webpage** — click a button in your browser, and an LED on your desk turns on. This is your first step into the hybrid architecture of the UNO Q: **Python** on the Linux processor handles the web server, while the **sketch** on the microcontroller controls the hardware. They talk to each other through the **Bridge**.

.. image:: img/led_result.png
   :width: 600
   :align: center
  
In this lesson, you will learn to:

* Understand the Python + Sketch hybrid architecture of App Lab
* Use the ``Bridge`` to call sketch functions from Python
* Build a web button that toggles an LED via Socket.IO
* Trace the full data path: browser → Python → Bridge → sketch → hardware

1. Build the Circuit
----------------------

**Components Needed**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_led` (Red)
     - 1 * :ref:`cpn_resistor` (220Ω)
     - Several :ref:`cpn_wires`
   * - |list_pan_tilt|
     - |list_red_led|
     - |list_220ohm|
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

Connect the LED (with 220Ω resistor) between **digital pin 5** and **GND** — the same circuit you built in the very first Module A lesson.

.. image:: /img/wiring/wiring_led.png
   :width: 500
   :align: center

2. Run the App
----------------


#. Download :download:`01 UI Control LED.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/01.UI.Control.LED.zip>`.
#. In App Lab, go to **Apps** → **Create new app** → **Import App** → **Import from Computer**, and open the package you downloaded.
#. Click the **Run** button (▶). A **Web UI** tab opens automatically.

#. You'll see a large circular button labeled "**LED IS OFF**". Click it — the LED lights up and the button glows teal with "**LED IS ON**". Click again to turn it off.

   .. image:: img/led_result.png
     :width: 600
     :align: center

**How it Works**

Now that you've seen the LED respond to your click, let's understand what's happening behind the scenes.

An App Lab project is a folder containing multiple files. Here's what each one does:

* ``01 UI Control LED/`` — the app folder

  * Bricks

    * WebUI-HTML

  * Sketch libraries

    * None — this project uses only built-in libraries

  * Files

    * ``assets/``

      * ``index.html`` — Web UI structure
      * ``app.js`` — Browser logic (Socket.IO client)
      * ``style.css`` — Visual styling
      * ``libs/`` — JavaScript libraries (Socket.IO)
      * ``fonts/``, ``img/`` — Static resources

    * ``python/``

      * ``main.py`` — Web server and Bridge communication

    * ``sketch/``

      * ``sketch.yaml`` — Sketch configuration
      * ``sketch.ino`` — Hardware control on the microcontroller

    * ``README.md`` — Project documentation and usage guide
    * ``app.yaml`` — App metadata (name, icon, bricks used)


The data path from click to LED — and back:


.. mermaid::

   sequenceDiagram
       participant B as Browser (HTML/JS)
       participant P as Python (main.py)
       participant S as Sketch (sketch.ino)

       B->>P: socket.emit('toggle_led')
       P->>P: toggle_led_state()
       P->>S: Bridge.call("set_led_state", True)
       S->>S: digitalWrite(5, HIGH)
       S-->>P: LED turns ON
       P-->>B: led_status_update
       B->>B: updateLedStatus()

Here's what each component does:

**Sketch (sketch.ino)** — runs on the STM32 MCU
  * Controls the hardware pin with ``digitalWrite()``
  * ``Bridge.provide()`` registers functions that Python can call
  * ``loop()`` is empty — everything is event-driven

**Python (main.py)** — runs on the Linux MPU
  * Hosts the ``WebUI`` server; browsers connect to it
  * ``ui.on_message()`` listens for button-click events from the browser
  * ``Bridge.call()`` sends commands to the sketch
  * ``ui.send_message()`` broadcasts status updates back to browsers

**Bridge** — communication channel between MPU and MCU
  * Sketch side: ``Bridge.provide("name", function)`` exposes a function
  * Python side: ``Bridge.call("name", args...)`` invokes it
  * This is RPC (Remote Procedure Call) — cross-processor function calls

**Browser (HTML/JS)** — runs in the user's browser
  * ``socket.emit()`` sends messages to Python when the button is clicked
  * ``socket.on()`` receives status updates and updates the button's visual state
  * The UI is a single circular button in ``index.html``, styled by ``style.css``


3. Experiment
----------------

**Change the Button Style**

In ``style.css``, modify the LED button's appearance:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Property
     - Try Changing
   * - ``width/height``
     - 200px for a larger button, 64px for a smaller one
   * - ``.led-on`` background
     - Change ``#29a3d9`` to ``#ff4444`` for a red glow
   * - ``box-shadow``
     - Increase the spread for a bigger glow effect
   * - ``transition`` duration
     - Change ``0.3s`` to ``0.1s`` for snappier response

**Add a Status Label**

Modify ``get_led_status()`` in ``main.py`` to include extra info:

.. code-block:: python

   def get_led_status():
       import time
       return {
           "led_is_on": led_is_on,
           "status_text": "LED IS ON" if led_is_on else "LED IS OFF",
           "timestamp": time.strftime("%H:%M:%S")
       }

Then update ``index.html`` to display the timestamp alongside the button.

4. Troubleshooting
--------------------

**Button clicks don't affect the LED**

* **Cause:** The Bridge connection isn't established, or the sketch function name doesn't match.
* **Solution:** Make sure ``Bridge.provide("set_led_state", ...)`` in the sketch matches ``Bridge.call("set_led_state", ...)`` in Python exactly — names are case-sensitive. Check the Monitor for Bridge connection errors.

**Button shows "LED IS ON" but the LED is actually off**

* **Cause:** The Python state (``led_is_on``) and the hardware state are out of sync.
* **Solution:** The ``get_led_state()`` function shows the Python variable, not the actual pin state. Add ``digitalRead(ledPin)`` in the sketch and expose it via another ``Bridge.provide()`` if you need true hardware feedback.

**Web UI shows "Connection to the board lost"**

* **Cause:** The Python web server stopped, or the browser can't reach the UNO Q.
* **Solution:** Check that the UNO Q is still running. Refresh the browser page. If using Wi-Fi mode, make sure both devices are on the same network. The error is handled by ``app.js``'s ``disconnect`` event.

**Page loads but shows no button**

* **Cause:** CSS or JavaScript files didn't load, or there's a syntax error in ``app.js``.
* **Solution:** Open the browser's Developer Tools (F12) and check the Console tab for errors. Verify that ``style.css`` and ``app.js`` are in the ``assets/`` folder and referenced correctly in ``index.html``.

5. Summary
-------------

You've built a web-controlled LED using the UNO Q's hybrid architecture! In this lesson, you learned:

* How Python (Linux), the sketch (MCU), and the browser work together
* How the Bridge enables RPC calls from Python to the sketch
* How Socket.IO provides real-time browser ↔ server communication
* How to trace a full data path across three processors

The pattern you learned — Python hosts the web UI, the sketch controls hardware, the Bridge connects them — is the foundation of every App Lab project in this module. In the next lesson, you'll extend this to control an RGB LED with a color picker.
