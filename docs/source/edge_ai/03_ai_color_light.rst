.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

03 AI Color Light
=================

In the face alarm project, the AI answered a yes-or-no question — is a face there? — and the buzzer had exactly one response. But real-world AI usually has to answer a richer question: not just *is something there*, but *what is it?* That is exactly what this project does. Point the camera at an apple, a banana, a water bottle, or a person — the model identifies the object, and the UNO Q lights an **RGB LED** in a matching color. Apple → red, banana → yellow, broccoli → green.

.. image:: img/03_ai_color_light.png
   :width: 600
   :align: center

In this lesson, you will learn to:

* Filter the object-detection results down to the objects your project cares about
* Map each recognized object to a **color code** and send it to the sketch over Bridge
* Turn that single code number into three PWM brightness values that mix the right color
* Watch the Web UI report the object name, color, and confidence in real time

1. Setup
--------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * :ref:`Pan Tilt Kit <pan_tilt_kit>`
     - 1 * :ref:`cpn_rgb_led`
     - 3 * :ref:`cpn_resistor` (220Ω)
     - 1 * USB-C Cable
   * - |list_pan_tilt|
     - |list_rgb_led|
     - |list_220ohm|
     - |list_usb_cable|

**Software Requirements**

This project uses the following Bricks:

* Bricks (declared in ``app.yaml``):

  * ``video_object_detection`` — runs the **general object-detection** model on every camera frame
  * ``web_ui`` — serves the Web UI with the live camera feed and the AI Result card

.. note::

   Before using the camera, make sure external carriers are enabled on your UNO Q — this is a one-time setup: :ref:`enable_external_carriers`.

**Wiring Diagram**

The RGB LED has **four legs**: the longest one is the **common cathode** — connect it to **GND** — and the other three are the red, green, and blue anodes, going to **D8**, **D7**, and **D6** respectively, each through its own 220Ω resistor. Never connect a channel directly to a pin without its resistor, or the LED can burn out.

.. image:: /img/wiring/wiring_rgb_led.png
   :width: 500
   :align: center

2. Run the App
--------------

#. Download :download:`03 AI Color Light.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/03.AI.Color.Light.zip>`.
#. In App Lab, go to **Apps** → **Create new app** → **Import App** → **Import from Computer**, and open the package you downloaded.
#. Click the **Run** button (▶). The sketch starts with the LED switched off, then the app boots the camera and loads the AI model — give it a few seconds before the video appears.
#. Open the **Web UI** tab: the live camera feed on the left (the status changes from **Connecting** to **Connected**) and the **AI Result** card on the right. Hold a real apple up to the camera — at 45% confidence the LED glows **red** and the card shows ``apple`` / **Red** / the confidence percentage. Try a banana, a water bottle, then a person: each mapped object lights its own color (yellow, blue, white). Take the object out of view and after about **2 seconds** the LED switches off.

.. image:: img/03_ai_color_light.png
   :width: 600
   :align: center

**How it Works**

You have just watched the LED choose a color on its own. Here is the path that decision travels, from a camera frame to colored light — and back to the page.

An App Lab project is a folder containing multiple files. Here's what each one does:

* ``03 AI Color Light/`` — the app folder

  * Bricks

    * ``video_object_detection`` — runs the general object-detection model on every camera frame, locally on the UNO Q
    * ``web_ui`` — serves the Web UI and pushes live updates to the browser

  * Sketch libraries

    * None — the sketch only uses the built-in Bridge library

  * Files

    * ``assets/``

      * ``index.html`` — Web UI structure (camera card and AI Result card)
      * ``app.js`` — Browser logic (Socket.IO client and card updates)
      * ``style.css`` — Visual styling
      * ``libs/`` — JavaScript libraries (Socket.IO)
      * ``img/`` — UI images (logo)
      * ``docs_assets/`` — Documentation images (result and wiring diagrams)

    * ``python/``

      * ``main.py`` — Camera, detection filtering, color mapping, and Bridge calls

    * ``sketch/``

      * ``sketch.yaml`` — Sketch configuration
      * ``sketch.ino`` — RGB LED control on the microcontroller

    * ``README.md`` — Project documentation and usage guide
    * ``app.yaml`` — App metadata (name, icon, bricks used)

The data path, from a camera frame to a lit RGB LED:

.. mermaid::

   sequenceDiagram
       participant C as Camera (CSI)
       participant P as Python (main.py)
       participant S as Sketch (sketch.ino)
       participant B as Browser (HTML/JS)

       C->>P: video frames
       P->>P: VideoObjectDetection → send_detections()
       P->>P: drop unmapped classes, keep the best confidence
       P->>S: Bridge.call("set_color", color_code)
       S->>S: setColor() → analogWrite() on D8/D7/D6
       P-->>B: object_color {object, color, hex, confidence}
       B->>B: update the AI Result card and the color swatch
       P->>S: 2 s without a mapped object → Bridge.call("set_color", 0)

Here's what each component does:

**Sketch (sketch.ino)** — runs on the STM32 MCU
  * ``setColor()`` is a ``switch`` over the color code it receives: 1 Red, 2 Yellow, 3 Orange, 4 Green, 5 Blue, 6 White, anything else Off
  * ``writeRgb()`` turns those three values into PWM brightness with ``analogWrite()`` on **D8**, **D7**, and **D6**

**Python (main.py)** — runs on the Linux MPU
  * ``VideoObjectDetection(camera, confidence=0.45, debounce_sec=0.3)`` runs the model locally, frame by frame
  * ``detection.on_detect_all(send_detections)`` hands every frame's results to your code

**Bridge** — the communication channel between the MPU and the MCU
  * Sketch side: ``Bridge.provide("set_color", setColor)`` exposes the color function
  * Python side: ``Bridge.call("set_color", color_code)`` invokes it with one integer

**Browser (HTML/JS)** — runs in the user's browser
  * ``socket.on('object_color', ...)`` writes the object name, the color name, and the confidence into the AI Result card
  * The HEX value that arrives with the same message paints the color swatch

3. Experiment
-------------

**Test the Mapped Objects**

Show each object to the camera and check the result:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Object
     - Expected Result
   * - A real apple
     - LED glows red; card shows ``apple`` / Red
   * - A banana
     - LED glows yellow; card shows ``banana`` / Yellow
   * - An orange
     - LED glows orange; card shows ``orange`` / Orange
   * - Broccoli
     - LED glows green; card shows ``broccoli`` / Green
   * - A water bottle
     - LED glows blue; card shows ``bottle`` / Blue
   * - A friend standing in front of the camera
     - LED glows white; card shows ``person`` / White

4. Troubleshooting
------------------

**The Web UI shows a black screen (no camera feed)**

* **Cause:** The camera is not enabled, or the camera cable is loose.
* **Solution:** Enable external carriers (see :ref:`enable_external_carriers`), then check the camera's FFC ribbon cable — the blue side faces up and both ends must click securely.

**The Web UI detects the object, but the LED never lights**

* **Cause:** The RGB LED is wired wrong.
* **Solution:** Check the legs: the longest leg is the common cathode and must go to GND; the red, green, and blue anodes go to D8, D7, and D6, each through its own 220Ω resistor.

**The LED lights the wrong color**

* **Cause:** The three channels are swapped — for example the red anode is on D6 instead of D8.
* **Solution:** Re-check each anode against its pin: Red → D8, Green → D7, Blue → D6.

5. Summary
----------

You just built a complete AI decision chain: the camera sees, the model classifies, Python chooses, and the LED obeys.

* How to filter detection results down to the classes your project responds to
* How to map each object to a single color code sent over Bridge — a small message that means a clear color
* How the sketch's ``setColor()`` switch turns the code into PWM values on three channels

In the next project the camera turns away from the desk and toward *you*.
