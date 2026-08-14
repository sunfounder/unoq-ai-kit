.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

06 Color Mixer
=============

So far, every LED you've controlled produced a single color — red. But color displays, stage lights, and smart bulbs can create millions of colors from just three primary ones: **red, green, and blue**. In this lesson, you'll use an **RGB LED** — three tiny LEDs (red, green, and blue) fused into one package — and control each channel independently with PWM to mix any color you want.

In this lesson, you will learn to:

* Control an RGB LED with three PWM channels simultaneously
* Write your first custom **function** — ``setColor()`` — to package reusable logic
* Understand **additive color mixing**: how red, green, and blue combine to form every other color
* Use parameters to make functions flexible and reusable

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

.. tip::

   The RGB LED has **four legs**. The longest leg is the **common cathode** (connect to GND). The other three legs are, from longest to shortest side: **Red**, **Ground (longest)**, **Green**, **Blue**.

**Wiring Diagram**

Follow the diagram below to place each component on the breadboard and connect the wires. Notice how the three resistors connect to three different PWM pins — each color channel gets its own independent control.

.. image:: /img/wiring/wiring_rgb_led.png
   :width: 500
   :align: center

.. warning::

   The RGB LED's **longest leg must go to GND**. The three shorter legs each connect to a separate PWM pin **through a 220Ω resistor**. Never connect an RGB LED pin directly to a digital pin without a resistor — each channel needs current limiting. Also, the flat edge of the LED package indicates the cathode side — use it to identify the correct orientation.

2. Code
----------

**Import and Run the Code**

All code for this course is provided as ``.zip`` files that you can import directly into App Lab.

#. Open **Arduino App Lab**, go to **My Apps**. Click the dropdown arrow next to **Create new app +** and select **Import App**.

   .. image:: /img/app_import_app.png
      :width: 600


#. Select **Import from Computer**.

   .. image:: /img/app_import_pc.png
      :width: 600


#. Navigate to the ``unoq-ai-kit/basic/`` folder and select ``06 Color Mixer.zip``. The app appears in **My Apps** — click it to open.

#. With the app open, click the **Run** button (▶) in the top-right corner.

   .. note::      
  
      This project uses the **RobotShield** library. see :ref:`install_update_lib_c` for installation or updating.
   
   .. image:: /img/app_run.png
      :width: 500


#. Wait a few seconds for the upload to finish. The RGB LED should cycle through eight colors — red, green, blue, yellow, cyan, magenta, white, and off — spending one second on each.

**The Sketch (sketch.ino)**

Now that you've seen the full color cycle in action, let's look at the sketch file.

.. code-block:: cpp
   :linenos:

   /*
    * Cycles through 8 colors using an RGB LED and 3-channel PWM.
    */

   #include "RobotShield.h"

   Pwm red(6);    // Red channel on P6
   Pwm green(5);  // Green channel on P5
   Pwm blue(4);   // Blue channel on P4

   void setup() {
       I2cBus::i2c().begin();

       red.begin();
       green.begin();
       blue.begin();

       red.setFreq(1000);
       green.setFreq(1000);
       blue.setFreq(1000);

       red.setEnable(true);
       green.setEnable(true);
       blue.setEnable(true);
   }

   // Set all three color channels at once
   // r, g, b: pulse width from 0 (off) to 1000 (full brightness)
   void setColor(uint16_t r, uint16_t g, uint16_t b) {
       red.setPulse(r);
       green.setPulse(g);
       blue.setPulse(b);
   }

   void loop() {
       setColor(1000, 0, 0);      // Red
       delay(1000);

       setColor(0, 1000, 0);      // Green
       delay(1000);

       setColor(0, 0, 1000);      // Blue
       delay(1000);

       setColor(1000, 1000, 0);   // Yellow   (red + green)
       delay(1000);

       setColor(0, 1000, 1000);   // Cyan     (green + blue)
       delay(1000);

       setColor(1000, 0, 1000);   // Magenta  (red + blue)
       delay(1000);

       setColor(1000, 1000, 1000);// White    (all three)
       delay(1000);

       setColor(0, 0, 0);         // Off      (none)
       delay(1000);
   }

**How it Works**

This lesson introduces your first custom function — a reusable block of code you write once and call many times:

.. code-block:: text

   setup() → runs once at startup:
       Initialize I2C bus (Robot Shield communication)
       Initialize 3 PWM channels (P6, P5, P4)
       Set each to 1000 Hz, enable all outputs

   loop() → runs over and over forever:
       For each of 8 colors:
           Call setColor(r, g, b) with that color's mix
           Wait 1000ms so the color is visible
       (then cycle repeats from Red)

#. Three PWM Objects for Three Color Channels

   - Three independent ``Pwm`` objects are created, one for each color channel — the same class used earlier for PWM output
   - Pin P6 controls red, pin P5 controls green, and pin P4 controls blue
   - Each channel receives its own pulse width value, allowing any combination of brightness across the three colors

   .. code-block:: arduino

      Pwm red(6);
      Pwm green(5);
      Pwm blue(4);

#. Setup: Initializing All Three Channels

   - All three channels are initialized with a common frequency of 1000 Hz and enabled for output
   - The I2C bus is started once, then each PWM channel is configured individually
   - This follows the same initialization pattern used for PWM output, repeated for each primary color

   .. code-block:: arduino

      void setup() {
          I2cBus::i2c().begin();
          red.begin();    green.begin();    blue.begin();
          red.setFreq(1000); green.setFreq(1000); blue.setFreq(1000);
          red.setEnable(true); green.setEnable(true); blue.setEnable(true);
      }

#. The Custom ``setColor()`` Function

   - This is a **function definition** — a reusable block of code with the name ``setColor``
   - ``void`` means it does not return a value; it just performs an action
   - The three parameters ``(r, g, b)`` accept the pulse width for each channel, and all three PWM channels are set in a single step

   .. code-block:: arduino

      void setColor(uint16_t r, uint16_t g, uint16_t b) {
          red.setPulse(r);
          green.setPulse(g);
          blue.setPulse(b);
      }

#. Calling the Function in the Loop

   - Each call to ``setColor()`` passes three numbers representing the brightness of red, green, and blue
   - ``setColor(1000, 0, 0)`` sends full pulse width to red and zero to the others, producing pure red
   - ``setColor(1000, 1000, 0)`` lights both red and green equally, producing yellow

   .. code-block:: arduino

      setColor(1000, 0, 0);      // Red
      delay(1000);
      setColor(0, 1000, 0);      // Green
      delay(1000);

#. Why Functions Matter

   - Without ``setColor()``, every color change would need three separate lines of code
   - With the function, each color is one clear, readable call — ``setColor(1000, 0, 0)``
   - Functions package logic into named, reusable blocks, making code shorter, cleaner, and easier to understand

   .. code-block:: arduino

      red.setPulse(1000);
      green.setPulse(0);
      blue.setPulse(0);

**Additive Color Mixing**

You've just discovered how screens and displays create every color you see. The RGB LED uses **additive color mixing** — starting from black (all off) and adding light to create colors:

.. list-table::
   :header-rows: 1
   :widths: 20 20 20 40

   * - Red
     - Green
     - Blue
     - Result
   * - 1000
     - 0
     - 0
     - Red
   * - 0
     - 1000
     - 0
     - Green
   * - 0
     - 0
     - 1000
     - Blue
   * - 1000
     - 1000
     - 0
     - Yellow (red + green)
   * - 0
     - 1000
     - 1000
     - Cyan (green + blue)
   * - 1000
     - 0
     - 1000
     - Magenta (red + blue)
   * - 1000
     - 1000
     - 1000
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

Pick a color that's not in the basic eight. Use values between 0 and 1000 for each channel to create something unique — orange, purple, pink, teal, warm white, or anything you can imagine. Add it to the cycle in ``loop()``.

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
      * - 1000
        - 200
        - 0
        - Orange
      * - 500
        - 0
        - 500
        - Purple
      * - 1000
        - 150
        - 300
        - Pink
      * - 0
        - 500
        - 500
        - Teal
      * - 1000
        - 600
        - 200
        - Warm gold
      * - 800
        - 1000
        - 0
        - Lime / chartreuse

   The exact look depends on your LED and resistors — experiment! Uneven values (like 1000, 200, 0 for orange) create the most interesting colors.


4. Troubleshooting
--------------------

**RGB LED does not light up at all**

* **Cause:** The common cathode (longest leg) is not connected to GND, or all three resistors are on the wrong legs.
* **Solution:** Check that the **longest leg** goes to the GND rail. The three shorter legs each need a 220Ω resistor to their respective PWM pins. Use a flat-head view: the flat edge of the LED identifies the cathode side.

**Only one or two colors work, others don't**

* **Cause:** A specific channel's resistor is loose, or the pin assignment is wrong.
* **Solution:** Test each channel individually — set the other two to 0 and verify that channel lights up on its own. Check that P6 drives red, P5 drives green, and P4 drives blue. Swap pins if needed.

**Colors look wrong (e.g., blue instead of red)**

* **Cause:** The RGB LED legs are misidentified — the channel-to-pin mapping is swapped.
* **Solution:** With the flat edge facing you and legs pointing down, the order is typically: Red → Ground (longest) → Green → Blue. If your LED's pinout differs, adjust the ``Pwm`` object declarations to match.

**RGB LED was bright for a moment, then died or a color stopped**

* **Cause:** A channel was connected without a resistor and burned out.
* **Solution:** The RGB LED needs a resistor on **each** of the three color pins. Replace the LED with a new one and double-check all three 220Ω resistors are in place before running again.


* **Cause:** The board is not connected, or App Lab can't find it.
* **Solution:** Check the USB-C cable is firmly connected at both ends. Try unplugging and re-plugging it. In App Lab, make sure your UNO Q is detected.

5. Summary
-------------

You just painted with light! In this lesson, you learned:

* How an RGB LED combines three independent LED elements into a single package
* How to control three PWM channels simultaneously — the foundation of color displays
* How to write and call your own **functions** with parameters — one of the most important skills in programming
* How **additive color mixing** works: red + green = yellow, green + blue = cyan, red + blue = magenta, all three = white
* How to create smooth color transitions by gradually changing PWM values in ``for`` loops

Functions are a game-changer — from now on, you can package complex logic into named, reusable blocks. In the next lesson, you'll control a DC motor — spinning a fan with speed and direction control using the Robot Shield's H-bridge.
