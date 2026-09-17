.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

06 Color Mixer
==============

So far, every LED you've controlled produced a single color — red. But color displays, stage lights, and smart bulbs can create millions of colors from just three primary ones: **red, green, and blue**. In this lesson, you'll use an **RGB LED** — three tiny LEDs (red, green, and blue) fused into one package — and control each channel independently with PWM to mix any color you want.

In this lesson, you will learn to:

* Control an RGB LED with three PWM channels simultaneously
* Write your first custom **function** — ``setColor()`` — to package reusable logic
* Understand **additive color mixing**: how red, green, and blue combine to form every other color
* Use parameters to make functions flexible and reusable

1. Setup
----------------------

**What You Need**

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

This project uses no external libraries — the sketch only uses the built-in Arduino framework.

**Wiring Diagram**

The RGB LED has **four legs**: the longest is the **common cathode** — connect it to **GND** — and the other three (Red, Green, Blue) go to **D8, D7, D6**, each channel through its own 220Ω resistor. Never connect a channel directly to a digital pin without a resistor — it burns out.

.. image:: /img/wiring/wiring_rgb_led.png
   :width: 500
   :align: center

2. Run the App
----------------

**Import and Run the Code**

All code for this course is provided as ``.zip`` files that you can import directly into App Lab.

#. Open **Arduino App Lab**, go to **Apps**. Click the dropdown arrow next to **Create new app +** and select **Import App**.

   .. image:: /img/app_import_app.png
      :width: 600


#. Select **Import from Computer**.

   .. image:: /img/app_import_pc.png
      :width: 600


#. Navigate to the ``unoq-ai-kit/basic/`` folder and select ``06 Color Mixer.zip``. The app appears in **Apps** — click it to open.

#. With the app open, click the **Run** button (▶) in the top-right corner.

   .. image:: /img/app_run.png
      :width: 500


#. Wait a few seconds for the upload to finish. The RGB LED should cycle through eight colors — red, green, blue, yellow, cyan, magenta, white, and off — spending one second on each.

**The Sketch (sketch.ino)**

Now that you've seen the full color cycle in action, let's look at the sketch file.

.. code-block:: cpp
   :linenos:

   /*
    * Cycles through 8 colors using an RGB LED and analogWrite().
    *
    * Red   -> D8
    * Green -> D7
    * Blue  -> D6
    */

   const int redPin = 8;
   const int greenPin = 7;
   const int bluePin = 6;

   void setup() {
       pinMode(redPin, OUTPUT);
       pinMode(greenPin, OUTPUT);
       pinMode(bluePin, OUTPUT);
   }

   // Set all three color channels at once
   // r, g, b: brightness from 0 (off) to 255 (full brightness)
   void setColor(int r, int g, int b) {
       analogWrite(redPin, r);
       analogWrite(greenPin, g);
       analogWrite(bluePin, b);
   }

   void loop() {
       setColor(255, 0, 0);      // Red
       delay(1000);

       setColor(0, 255, 0);      // Green
       delay(1000);

       setColor(0, 0, 255);      // Blue
       delay(1000);

       setColor(255, 255, 0);    // Yellow   (red + green)
       delay(1000);

       setColor(0, 255, 255);    // Cyan     (green + blue)
       delay(1000);

       setColor(255, 0, 255);    // Magenta  (red + blue)
       delay(1000);

       setColor(255, 255, 255);  // White    (all three)
       delay(1000);

       setColor(0, 0, 0);        // Off      (none)
       delay(1000);
   }

**How it Works**

This lesson introduces your first custom function — a reusable block of code you write once and call many times:

.. code-block:: text

   setup() → runs once at startup:
       Set pins 8, 7, and 6 as OUTPUT
       (red, green, and blue channels)

   loop() → runs over and over forever:
       For each of 8 colors:
           Call setColor(r, g, b) with that color's mix
           Wait 1000ms so the color is visible
       (then cycle repeats from Red)

#. Three Pin Constants for Three Color Channels

   - Three ``const int`` pin constants are created, one for each color channel — giving each pin a meaningful name
   - Pin 8 controls red, pin 7 controls green, and pin 6 controls blue
   - Each channel receives its own brightness value, allowing any combination of brightness across the three colors

   .. code-block:: arduino

      const int redPin = 8;
      const int greenPin = 7;
      const int bluePin = 6;

#. Setup: Configuring All Three Channels as Outputs

   - All three channels are set to ``OUTPUT`` mode so they can drive the LED
   - ``pinMode()`` tells the microcontroller that each pin should send signals out to the LED
   - This follows the same ``pinMode()`` pattern you used in earlier lessons, repeated for each primary color

   .. code-block:: arduino

      void setup() {
          pinMode(redPin, OUTPUT);
          pinMode(greenPin, OUTPUT);
          pinMode(bluePin, OUTPUT);
      }

#. The Custom ``setColor()`` Function

   - This is a **function definition** — a reusable block of code with the name ``setColor``
   - ``void`` means it does not return a value; it just performs an action
   - The three parameters ``(r, g, b)`` accept the brightness for each channel, and all three channels are set in a single step

   .. code-block:: arduino

      void setColor(int r, int g, int b) {
          analogWrite(redPin, r);
          analogWrite(greenPin, g);
          analogWrite(bluePin, b);
      }

#. Calling the Function in the Loop

   - Each call to ``setColor()`` passes three numbers representing the brightness of red, green, and blue
   - ``setColor(255, 0, 0)`` sends full brightness to red and zero to the others, producing pure red
   - ``setColor(255, 255, 0)`` lights both red and green equally, producing yellow

   .. code-block:: arduino

      setColor(255, 0, 0);      // Red
      delay(1000);
      setColor(0, 255, 0);      // Green
      delay(1000);

#. Why Functions Matter

   - Without ``setColor()``, every color change would need three separate lines of code
   - With the function, each color is one clear, readable call — ``setColor(255, 0, 0)``
   - Functions package logic into named, reusable blocks, making code shorter, cleaner, and easier to understand

   .. code-block:: arduino

      analogWrite(redPin, 255);
      analogWrite(greenPin, 0);
      analogWrite(bluePin, 0);

**Additive Color Mixing**

You've just discovered how screens and displays create every color you see. The RGB LED uses **additive color mixing** — starting from black (all off) and adding light to create colors:

.. list-table::
   :header-rows: 1
   :widths: 20 20 20 40

   * - Red
     - Green
     - Blue
     - Result
   * - 255
     - 0
     - 0
     - Red
   * - 0
     - 255
     - 0
     - Green
   * - 0
     - 0
     - 255
     - Blue
   * - 255
     - 255
     - 0
     - Yellow (red + green)
   * - 0
     - 255
     - 255
     - Cyan (green + blue)
   * - 255
     - 0
     - 255
     - Magenta (red + blue)
   * - 255
     - 255
     - 255
     - White (all three)
   * - 0
     - 0
     - 0
     - Off

This is the same principle behind every pixel in your phone, computer, and TV screen — millions of tiny RGB elements, each independently controlled to form the image you see.

3. Experiment
----------------

**Change the Cycle Speed**

Try adjusting the ``delay()`` after each color to change the cycle speed:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Delay
     - Effect
   * - ``delay(500)``
     - Fast cycle — colors flash by twice per second
   * - ``delay(2000)``
     - Slow cycle — each color lingers for 2 seconds
   * - ``delay(100)``
     - Strobe effect — very fast, almost flickering

**Challenge: Create Your Own Color**

Pick a color that's not in the basic eight. Use values between 0 and 255 for each channel to create something unique — orange, purple, pink, teal, warm white, or anything you can imagine. Add it to the cycle in ``loop()``.

.. dropdown:: Click to reveal hints
   :open:

   Try these mixtures as starting points:

   .. list-table::
      :header-rows: 1
      :widths: 20 20 20 40

      * - Red
        - Green
        - Blue
        - Approximate Color
      * - 255
        - ~50
        - 0
        - Orange
      * - ~130
        - 0
        - ~130
        - Purple
      * - 255
        - ~40
        - ~75
        - Pink
      * - 0
        - ~130
        - ~130
        - Teal
      * - 255
        - ~155
        - ~50
        - Warm gold
      * - ~205
        - 255
        - 0
        - Lime / chartreuse

   The exact look depends on your LED and resistors — experiment! Uneven values (like 255, ~50, 0 for orange) create the most interesting colors.


4. Troubleshooting
--------------------

**RGB LED does not light up at all**

* **Cause:** The common cathode (longest leg) is not connected to GND, or all three resistors are on the wrong legs.
* **Solution:** Check that the **longest leg** goes to the GND rail. The three shorter legs each need a 220Ω resistor to their respective PWM pins. Use a flat-head view: the flat edge of the LED identifies the cathode side.

**Only one or two colors work, others don't**

* **Cause:** A specific channel's resistor is loose, or the pin assignment is wrong.
* **Solution:** Test each channel individually — set the other two to 0 and verify that channel lights up on its own. Check that D8 drives red, D7 drives green, and D6 drives blue. Swap pins if needed.

**Colors look wrong (e.g., blue instead of red)**

* **Cause:** The RGB LED legs are misidentified — the channel-to-pin mapping is swapped.
* **Solution:** With the flat edge facing you and legs pointing down, the order is typically: Red → Ground (longest) → Green → Blue. If your LED's pinout differs, adjust the pin constants at the top of the sketch to match.

**RGB LED was bright for a moment, then died or a color stopped**

* **Cause:** A channel was connected without a resistor and burned out.
* **Solution:** The RGB LED needs a resistor on **each** of the three color pins. Replace the LED with a new one and double-check all three 220Ω resistors are in place before running again.

5. Summary
-------------

You just painted with light! In this lesson, you learned:

* How an RGB LED combines three independent LED elements into a single package
* How to control three PWM channels simultaneously — the foundation of color displays
* How to write and call your own **functions** with parameters — one of the most important skills in programming
* How **additive color mixing** works: red + green = yellow, green + blue = cyan, red + blue = magenta, all three = white
* How to cycle through eight colors with one ``setColor()`` call per second

Functions are a game-changer — from now on, you can package complex logic into named, reusable blocks. In the next lesson, you'll control a DC motor — spinning a fan with speed and direction control using the Robot Shield's H-bridge.
