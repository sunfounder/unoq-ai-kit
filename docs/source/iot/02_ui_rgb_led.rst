.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

02 UI Control RGB LED
==========================

A single on/off button is useful. But what if you want to pick any color? In this lesson, you'll build a **web color picker** that controls an RGB LED — spin a color wheel and adjust the brightness, and the LED mixes the colors in real time. The same hybrid architecture from the previous lesson (Python + Bridge + Sketch) now drives three PWM channels on the Robot Shield instead of one digital pin.

.. image:: img/rgb_result.png
   :width: 600
   :align: center

In this lesson, you will learn to:

* Send multiple numeric values (0–255) from browser to sketch via Python
* Control three PWM channels with the Robot Shield's ``Pwm`` class
* Convert colors between the web's HSV model and the hardware's RGB channels
* Map web-standard 0–255 values to the Robot Shield's 0–1000 PWM range

1. Build the Circuit
----------------------

**Components Needed**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_rgb_led`
     - 3 * :ref:`cpn_resistor` (220Ω)
     - Several :ref:`cpn_wires`
   * - |list_pan_tilt|
     - |list_rgb_led|
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

**Software Requirements**

This project uses the following Bricks and sketch libraries:

* Bricks (declared in ``app.yaml``):

  * ``web_ui`` — serves the Web UI and pushes live colour updates to the browser
* Libraries (declared in ``sketch.yaml``):

  * ``RobotShield`` (1.0.4) — access to the Robot Shield's GPIO, PWM, and I2C hardware

.. note::

   An RGB LED is three LEDs (red, green, blue) in one package. It has four pins: one common cathode (longest pin) and three anodes, each needing its own 220Ω current-limiting resistor.

**Wiring Diagram**

#. Connect the RGB LED's **common cathode** (longest pin, flat edge side) to **GND**.

#. Connect the **red** anode → 220Ω → **D8**. **Green** anode → 220Ω → **D7**. **Blue** anode → 220Ω → **D6**. These are PWM channels on the Robot Shield.

.. image:: /img/wiring/wiring_rgb_led.png
   :width: 500
   :align: center

2. Run the App
----------------


#. Download :download:`02 UI Control RGB LED.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/02.UI.Control.RGB.LED.zip>`.
#. In App Lab, go to **Apps** → **Create new app** → **Import App** → **Import from Computer**, and open the package you downloaded.
#. Click the **Run** button (▶). The Web UI opens with a color wheel, a brightness slider, and a preview circle.

#. Drag around the wheel — the LED and the preview change color together. Slide the brightness up and down. Try: pure red (top of the wheel), orange (between red and yellow), cyan, and magenta.

.. image:: img/rgb_result.png
   :width: 600
   :align: center

**How it Works**

A color wheel is a circle of hues — the browser turns your selection into R/G/B numbers, Python relays them, and the sketch drives three PWM channels:

* ``02 UI Control RGB LED/`` — the app folder

  * Files

    * ``assets/``

      * ``index.html`` — color wheel canvas, brightness slider, preview circle
      * ``app.js`` — HSV→RGB conversion and Socket.IO events
      * ``style.css`` — Visual styling

    * ``python/``

      * ``main.py`` — Web UI server and Bridge relay

    * ``sketch/``

      * ``sketch.ino`` — RobotShield PWM control

    * ``app.yaml`` — App metadata (name, icon, bricks used)

.. mermaid::

   sequenceDiagram
       participant B as Browser (HTML/JS)
       participant P as Python (main.py)
       participant S as Sketch (sketch.ino)

       B->>B: wheel drag → HSV → {r, g, b} (0–255)
       B->>P: socket.emit('set_rgb_color', {r, g, b})
       P->>S: Bridge.call("set_rgb_color", r, g, b)
       S->>S: map 0–255 → 0–1000, setPulse on D8/D7/D6
       P-->>B: rgb_status_update
       B->>B: update preview circle

Here's what each component does:

**Sketch (sketch.ino)** — runs on the STM32 MCU
  * Creates three ``Pwm`` objects: ``red(8)``, ``green(7)``, ``blue(6)`` — red on **D8**, green on **D7**, blue on **D6**
  * Initializes I2C (``I2cBus::i2c().begin()``) and sets each channel to 1000 Hz
  * ``Bridge.provide("set_rgb_color", set_rgb_color)`` registers the function Python calls
  * ``set_rgb_color()`` maps web-standard 0–255 values to the Robot Shield's 0–1000 pulse range with ``map(r, 0, 255, 0, 1000)``

**Python (main.py)** — runs on the Linux MPU
  * Keeps the current color in a ``rgb_color`` dictionary
  * ``ui.on_message("set_rgb_color", ...)`` receives the browser's R/G/B values
  * Calls ``Bridge.call("set_rgb_color", r, g, b)`` and broadcasts ``rgb_status_update`` back to all browsers

**Browser (HTML/JS)** — runs in the user's browser
  * The color wheel is a canvas: your drag position becomes **hue** (angle) and **saturation** (distance from center); the slider controls **brightness**
  * ``hsvToRgb()`` converts HSV to R/G/B values (0–255) — the browser speaks HSV, the hardware speaks RGB
  * Sends only when the color actually changed (``lastSent`` dedupe), keeping Bridge traffic light while dragging

**Two color models, one LED**

Humans think of color as "which hue, how vivid, how bright" — that's HSV, and it's what a color wheel naturally represents. LEDs physically mix red, green, and blue light. The conversion happens in the browser before the values even leave the page — the sketch only ever sees three numbers.

3. Experiment
----------------

**Add Preset Color Buttons**

In ``index.html``, add preset buttons below the color wheel. In ``app.js``:

.. code-block:: javascript

   function setPreset(r, g, b) {
       socket.emit('set_rgb_color', { r: r, g: g, b: b });
   }

   document.getElementById('preset-orange').addEventListener('click',
       () => setPreset(255, 100, 0));

**Challenge: Color Fade Animation**

Add a "Fade" button in the HTML. In ``app.js``, animate between two colors over 3 seconds using ``setInterval`` — send incremental R/G/B values at ~30 FPS. The smooth transition is handled entirely in the browser; the sketch just receives the stream of updated values.

4. Troubleshooting
--------------------

**LED shows wrong colors — red is green, etc.**

* **Cause:** The RGB LED pins are connected in the wrong order.
* **Solution:** Check: red anode → D8, green → D7, blue → D6. RGB LEDs have four pins — the longest is common cathode (GND). The three shorter pins are the color anodes.

**The LED stays dark or only one color works**

* **Cause:** A channel is not initialized, or the I2C bus is not started.
* **Solution:** Verify ``I2cBus::i2c().begin()`` is called in ``setup()`` before the PWM channels, and that each ``Pwm`` object called ``begin()`` and ``setEnable(true)``. The Robot Shield's PWM channels communicate over I2C — without it, nothing reaches the LED.

**Preview updates but LED doesn't change**

* **Cause:** ``Bridge.call("set_rgb_color", ...)`` isn't reaching the sketch.
* **Solution:** Check that the function name matches exactly — ``Bridge.provide("set_rgb_color", ...)`` in the sketch and ``Bridge.call("set_rgb_color", ...)`` in Python. Names are case-sensitive. Open the Monitor for Bridge errors.

**Color jumps while dragging the wheel**

* **Cause:** The browser sends more updates than the Bridge can keep up with.
* **Solution:** The sketch already dedupes identical colors (``lastSent``). If it still feels jumpy, close other apps that are loading the network, or reduce the brightness-slider update rate.

5. Summary
-------------

You've built a real-time web color mixer! In this lesson, you learned:

* How to pass multiple numeric parameters through ``Bridge.call()``
* How to drive three Robot Shield PWM channels with the ``Pwm`` class
* How the browser converts HSV (color wheel) into RGB (LED channels)
* How to map web-standard 0–255 values to the Robot Shield's 0–1000 PWM range

In the next lesson, you'll reverse the data flow — a sensor on your desk will stream its readings to a live dashboard in your browser.
