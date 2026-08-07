.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

2. UI Control RGB LED
=========================

A single on/off button is useful. But what if you want to pick any color? In this lesson, you'll build a **web color picker** that controls an RGB LED — drag sliders for red, green, and blue, and the LED mixes the colors in real time. The same hybrid architecture from Lesson 1 (Python + Bridge + Sketch) now handles three PWM channels instead of one digital pin.

In this lesson, you will learn to:

* Send multiple numeric values (0–255) from browser to sketch via Python
* Control three PWM channels with ``analogWrite()`` through Bridge calls
* Update multiple UI elements simultaneously based on hardware state
* Build a real-time color preview in the browser

1. Build the Circuit
----------------------

**Components Needed**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * :ref:`Arduino Uno Q <cpn_uno_q>`
     - 1 * :ref:`cpn_rgb_led`
     - 3 * :ref:`cpn_resistor` (220Ω)
     - Several :ref:`cpn_wires`
   * - |list_uno_q|
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

.. note::

   An RGB LED is three LEDs (red, green, blue) in one package. It has four pins: one common cathode (longest pin) and three anodes, each needing its own 220Ω current-limiting resistor.

**Wiring Diagram**

.. image:: img/2_ui_rgb_led_fritzing.png
   :width: 700
   :align: center

#. Connect the RGB LED's **common cathode** (longest pin, flat edge side) to **GND**.

#. Connect the **red** anode → 220Ω → **pin 9** (PWM). **Green** anode → 220Ω → **pin 10** (PWM). **Blue** anode → 220Ω → **pin 11** (PWM).

2. Code
----------

**Import the Code**

#. In App Lab, go to **My Apps** → **Import App** → **Import from Computer**.

#. Navigate to ``unoq-ai-kit/iot/`` and select ``2_ui_rgb_led.zip``. Open it.

**Run the Code**

#. Click the **Run** button (▶). The Web UI opens with three sliders (R, G, B) and a color preview circle.

#. Drag **Red** to 255 — the LED glows red and the preview turns red. Add **Green** — the color shifts to yellow. Add **Blue** — it becomes white.

#. Try: R=255 G=100 B=0 (orange), R=0 G=255 B=255 (cyan), R=255 G=0 B=255 (magenta).

.. image:: img/2_ui_rgb_led_result.gif
   :width: 600
   :align: center

**The Code — sketch.ino**

Three PWM pins, three Bridge functions:

.. code-block:: cpp
   :linenos:

   #include <Arduino_RouterBridge.h>

   const int redPin = 9;
   const int greenPin = 10;
   const int bluePin = 11;

   void setup() {
       Monitor.begin();
       pinMode(redPin, OUTPUT);
       pinMode(greenPin, OUTPUT);
       pinMode(bluePin, OUTPUT);

       Bridge.begin();
       Bridge.provide("set_color", set_color);
       Bridge.provide("get_color", get_color);
   }

   void loop() {}

   void set_color(int r, int g, int b) {
       analogWrite(redPin, r);
       analogWrite(greenPin, g);
       analogWrite(bluePin, b);
   }

   String get_color() {
       // Return nothing for now — state is tracked in Python
       return "";
   }

.. note::

   ``Bridge.provide()`` functions can take multiple parameters. ``set_color(int r, int g, int b)`` receives all three slider values in one call, avoiding three separate Bridge calls.

**The Code — main.py**

Python receives slider changes from the browser and forwards them to the sketch:

.. code-block:: python
   :linenos:

   from arduino.app_utils import *
   from arduino.app_bricks.web_ui import WebUI

   current_color = {"r": 0, "g": 0, "b": 0}

   def get_color_status():
       return {
           "r": current_color["r"],
           "g": current_color["g"],
           "b": current_color["b"]
       }

   def on_color_change(client, data):
       global current_color
       r = int(data.get("r", 0))
       g = int(data.get("g", 0))
       b = int(data.get("b", 0))

       current_color = {"r": r, "g": g, "b": b}

       Bridge.call("set_color", r, g, b)
       ui.send_message('color_update', get_color_status())

   def on_get_initial_state(client, data):
       ui.send_message('color_update', get_color_status(), client)

   ui = WebUI()
   ui.on_message('color_change', on_color_change)
   ui.on_message('get_initial_state', on_get_initial_state)

   App.run()

**The Code — app.js (key parts)**

Three range sliders, each sending values on change:

.. code-block:: javascript

   const redSlider = document.getElementById('red-slider');
   const greenSlider = document.getElementById('green-slider');
   const blueSlider = document.getElementById('blue-slider');
   const preview = document.getElementById('color-preview');

   function sendColor() {
       socket.emit('color_change', {
           r: parseInt(redSlider.value),
           g: parseInt(greenSlider.value),
           b: parseInt(blueSlider.value)
       });
   }

   redSlider.addEventListener('input', sendColor);
   greenSlider.addEventListener('input', sendColor);
   blueSlider.addEventListener('input', sendColor);

   socket.on('color_update', (msg) => {
       redSlider.value = msg.r;
       greenSlider.value = msg.g;
       blueSlider.value = msg.b;
       preview.style.backgroundColor = `rgb(${msg.r},${msg.g},${msg.b})`;
   });

**How it Works**

.. mermaid::

   sequenceDiagram
       participant B as Browser (HTML/JS)
       participant P as Python (main.py)
       participant S as Sketch (sketch.ino)

       B->>P: socket.emit('color_change', {r:200, g:0, b:0})
       P->>S: Bridge.call("set_color", 200, 0, 0)
       S->>S: analogWrite(9,200); analogWrite(10,0); analogWrite(11,0)
       S-->>P: LED = red
       P-->>B: color_update
       B->>B: preview.style = rgb(200,0,0)

The key difference from Lesson 1: **three numeric values** instead of one boolean. ``Bridge.call("set_color", r, g, b)`` passes multiple parameters. ``ui.send_message()`` sends a dictionary that the browser uses to update all three sliders and the preview simultaneously.

3. Experiment
----------------

**Add Preset Color Buttons**

In ``index.html``, add preset buttons below the sliders. In ``app.js``:

.. code-block:: javascript

   function setPreset(r, g, b) {
       redSlider.value = r; greenSlider.value = g; blueSlider.value = b;
       sendColor();
   }

   document.getElementById('preset-orange').addEventListener('click',
       () => setPreset(255, 100, 0));

**Challenge: Color Fade Animation**

Add a "Fade" button in the HTML. In ``app.js``, animate between two colors over 3 seconds using ``requestAnimationFrame`` or ``setInterval`` — send incremental color values to Python at ~30 FPS. The smooth transition is handled entirely in the browser; the sketch just receives the stream of updated values.

4. Troubleshooting
--------------------

**LED shows wrong colors — red is green, etc.**

* **Cause:** The RGB LED pins are connected in the wrong order.
* **Solution:** Check: red anode → pin 9, green → pin 10, blue → pin 11. RGB LEDs have four pins — the longest is common cathode (GND). The three shorter pins are the color anodes.

**Slider movement feels laggy**

* **Cause:** Too many Bridge calls per second.
* **Solution:** Each slider ``input`` event fires continuously during a drag (~60 events/second). Add a throttle in ``app.js``: only send once every 50ms. This reduces Bridge calls without visible quality loss.

**Color preview updates but LED doesn't change**

* **Cause:** ``Bridge.call("set_color", ...)`` isn't reaching the sketch, or the pins aren't PWM-capable.
* **Solution:** Verify that pins 9, 10, 11 are PWM-capable on the UNO Q. Check Monitor for Bridge errors. Try adding ``Monitor.println()`` in ``set_color()`` to confirm the sketch is receiving calls.

5. Summary
-------------

You've built a real-time web color mixer! In this lesson, you learned:

* How to pass multiple numeric parameters through ``Bridge.call()``
* How to handle multi-value messages in Python and relay them to the sketch
* How to sync three UI sliders with hardware PWM output
* How to throttle rapid UI events for reliable Bridge communication

In the next lesson, you'll go beyond local control — using Arduino Cloud to play musical notes on a buzzer from anywhere with internet access.
