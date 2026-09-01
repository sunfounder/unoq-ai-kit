.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

05 Voice-Controlled RGB LED
=============================

Earlier, you mixed colors by writing PWM values into three pins. Now your voice picks the color. Hold the button, say "Turn on the blue light", release it — the board recognizes the color name and lights the RGB LED. Speech is no longer just text on a screen; it drives hardware.

In this lesson, you will learn to:

* Search recognized text for color keywords
* Send a recognized command from Python to the sketch with ``Bridge.call()``
* Map color names to PWM values in the sketch
* Check the most important keyword first so commands don't collide

1. Setup
----------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_rgb_led`
     - 3 * :ref:`cpn_resistor` (220Ω)
     - 1 * :ref:`cpn_button`
   * - |list_pan_tilt|
     - |list_rgb_led|
     - |list_220ohm|
     - |list_button|
   * - 1 * :ref:`cpn_breadboard`
     - Several :ref:`cpn_wires`
     - 1 * USB Cable
     - -
   * - |list_breadboard|
     - |list_wire|
     - |list_usb_cable|
     - -

**Software Requirements**

This project uses the following App Lab Brick:

* Bricks:

  * ``sunfounder_stt`` (local speech-to-text, Whisper model)

.. note::

   The project ZIP is large (about 100 MB) because it bundles the local speech recognition model. The first import takes a while — this is normal.

**Wiring Diagram**

Connect the push button between D2 and GND — no external resistor is needed, the sketch uses the internal pull-up resistor. Connect each RGB LED channel to its pin through a 220Ω resistor:

- Button pin 1 → **D2**
- Button pin 2 → **GND**
- RGB LED **R** → 220Ω → **D8**
- RGB LED **G** → 220Ω → **D7**
- RGB LED **B** → 220Ω → **D6**

.. image:: /img/wiring/wiring_button_rgb.png
   :width: 500
   :align: center

2. Run the App
----------------

#. Open **Arduino App Lab**, import ``05 Voice-Controlled RGB LED.zip`` from the ``unoq-ai-kit/media/`` folder.

#. Click **Run** (▶). The RGB LED flashes red → green → blue → off as a wiring test, and the Output window shows:

   *"Local STT is ready."*

#. Hold the button, say a color command — for example, "Turn on the blue light" — then release the button. The RGB LED glows blue and the Output window shows **Light set to blue.**

**How it Works**

The recognized speech is searched for keywords, and only the color name travels to the sketch:

.. mermaid::

   sequenceDiagram
       participant B as Button (D2)
       participant S as Sketch (sketch.ino)
       participant P as Python (main.py)

       Note over P: press edge → stt.start_listening()
       Note over P: release edge → stt.stop_listening()
       P->>P: stt.get_result() → "Turn on the blue light."
       P->>P: "off" checked first
       P->>P: "blue" found in SUPPORTED_COLORS
       P->>S: Bridge.call("set_color", "blue")
       S->>S: analogWrite(D8, D7, D6)
       S-->>P: RGB LED glows blue

**Python (main.py)** — runs on the Linux MPU

* The recognized text is converted to lowercase, so "BLUE", "Blue", and "blue" all match. Then Python looks for each keyword inside the whole sentence — a single word ("blue") and a full sentence ("Turn on the blue light.") both work.
* ``"off"`` is checked **first** before the color list. Otherwise the word "off" could never be found — it isn't a color in ``SUPPORTED_COLORS`` at all.
* If no keyword matches, Python prints a hint listing every supported color and the LED stays unchanged.
* Python never touches PWM values — it only sends the color name. The sketch decides what each color means in voltages.

**Sketch (sketch.ino)** — runs on the STM32 MCU

The sketch receives a color name and converts it into three PWM values:

.. code-block:: cpp

   void setColor(String color)
   {
       String selectedColor = color;
       selectedColor.toLowerCase();

       if (selectedColor == "red") {
           setRgb(255, 0, 0);
       } else if (selectedColor == "green") {
           setRgb(0, 255, 0);
       } else if (selectedColor == "blue") {
           setRgb(0, 0, 255);
       } else if (selectedColor == "yellow") {
           setRgb(255, 180, 0);
       } else if (selectedColor == "cyan") {
           setRgb(0, 255, 255);
       } else if (selectedColor == "purple") {
           setRgb(128, 0, 180);
       } else if (selectedColor == "white") {
           setRgb(255, 255, 255);
       } else {
           setRgb(0, 0, 0);   // off
       }
   }

* Each color is a (red, green, blue) mix where every value ranges from 0 to 255 — the same PWM mixing you used in the Color Mixer project earlier.
* ``setRgb()`` writes the three values to D8, D7, D6 with ``analogWrite()``.
* On startup, ``setup()`` flashes red → green → blue → off so you can verify the wiring before speaking a single word.

3. Experiment
----------------

**Try Every Command**

Speak different color commands and watch the LED:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - You say
     - Expected result
   * - "Turn on the red light."
     - LED glows red; Output shows ``Light set to red.``
   * - "blue"
     - LED glows blue; Output shows ``Light set to blue.``
   * - "Make it purple please"
     - LED glows purple; Output shows ``Light set to purple.``
   * - "Turn off the light."
     - LED turns off; Output shows ``Light turned off.``
   * - "Show me orange"
     - Nothing changes; Output lists the supported colors

**Adjust a Color Mix**

In ``sketch.ino``, change the PWM values for ``yellow``:

.. code-block:: cpp

   } else if (color == "yellow") {
       setRgb(255, 120, 0);   // deeper orange-yellow
   }

The LED now shows your custom shade — the voice command stays the same.

**Challenge: Add a New Color**

Add ``pink`` to both sides of the system:

* In ``main.py``, add ``"pink"`` to ``SUPPORTED_COLORS``.
* In ``sketch.ino``, add a ``else if (color == "pink")`` branch with your own mix, for example ``setRgb(255, 105, 180)``.

Run again and say "pink" — if the LED lights, your Python and sketch changes are working together.

4. Troubleshooting
--------------------

**The LED shows the wrong color**

* **Cause:** The R, G, B wires are swapped or connected to the wrong pins.
* **Solution:** Check R→220Ω→D8, G→220Ω→D7, B→220Ω→D6 against the wiring diagram. The startup flash (red → green → blue) helps: if the first flash isn't red, the channels are swapped.

**The LED never lights up**

* **Cause:** The RGB LED module's ground pin isn't connected, or the module requires it.
* **Solution:** Connect the RGB LED ground pin to GND when required by your module — some modules share one ground, others have a pin per channel.

**Saying "Turn off the light" changes nothing**

* **Cause:** The word "off" wasn't found in the recognized text.
* **Solution:** Speak clearly and make sure "off" is in the sentence. The keyword search needs the exact word — "shut down" or "stop" won't match.

**Every command prints the hint list**

* **Cause:** The recognized text doesn't contain any supported color keyword.
* **Solution:** Use the exact keywords: red, green, blue, yellow, cyan, purple, white, off. Avoid phrases like "make it darker" that contain no keyword.

5. Summary
-------------

Your voice now controls real hardware! In this lesson, you learned:

* How to search recognized speech for keywords with ``in``
* Why ``"off"`` must be checked before the color list
* How Python sends color names to the sketch with ``Bridge.call()``
* How the sketch maps color names to PWM values on D8, D7, D6

In the next lesson, the board answers back — it will recognize your speech and repeat it aloud through the speaker.
