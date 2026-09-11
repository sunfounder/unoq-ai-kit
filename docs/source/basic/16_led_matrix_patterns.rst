.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

16 LED Matrix Patterns
======================

So far, every output you've controlled has been a single component — an LED, a buzzer, a motor. Now you'll control a grid of 104 tiny LEDs arranged in 8 rows and 13 columns, built right into the UNO Q board. Display a heart, a star, a smile, an arrow, or a check mark — each pattern stored as a simple grid of 1s and 0s. No breadboard, no wires, no external components. Everything you need is on the board itself.

In this lesson, you will learn to:

* Use the UNO Q's built-in **8×13 LED matrix**
* Store bitmap patterns as ``uint8_t`` arrays in a separate **header file**
* Use the ``Arduino_LED_Matrix`` library to render bitmap data
* Organize code by separating **data** (patterns) from **logic** (the sketch)

1. Setup
----------------------

**What You Need**

.. list-table::
   :widths: 25 25
   :header-rows: 0

   * - 1 * UNO Q
     - 1 * USB Cable
   * - |list_pan_tilt|
     - |list_usb_cable|

**Software Requirements**

This project uses no external libraries — the sketch only uses the built-in Arduino framework.

No breadboard wiring is needed — the 8×13 LED matrix is built into the UNO Q board, the grid of tiny white dots above the pin labels, and everything in this lesson runs on the board itself.


2. Run the App
----------------

**Import and Run the Code**

#. Open **Arduino App Lab**, go to **Apps**. Click the dropdown arrow next to **Create new app +** and select **Import App**.

   .. image:: /img/app_import_app.png
      :width: 600

#. Select **Import from Computer**.

   .. image:: /img/app_import_pc.png
      :width: 600

#. Navigate to the ``unoq-ai-kit/basic/`` folder and select ``16 LED Matrix Patterns.zip``. The app appears in **Apps** — click it to open.

#. Click the **Run** button (▶) in the top-right corner.

   .. image:: /img/app_run.png
      :width: 500

#. Wait a few seconds for the upload to finish. Five patterns cycle continuously on the LED matrix — heart, star, smile, arrow, and check mark — one second per pattern.

**The Sketch (sketch.ino)**

Now that you've seen the pattern cycle, let's look at the sketch file.

.. code-block:: cpp
   :linenos:

   /*
    * LED Matrix Patterns
    *
    * Displays five simple patterns in sequence:
    * Heart -> Star -> Smile -> Arrow -> Check
    */

   #include <Arduino_LED_Matrix.h>
   #include "matrix_patterns.h"

   Arduino_LED_Matrix matrix;

   const unsigned long DISPLAY_TIME = 1000;

   void showPattern(uint8_t pattern[8][13]) {
       matrix.renderBitmap(pattern, 8, 13);
       delay(DISPLAY_TIME);
   }

   void setup() {
       matrix.begin();
       matrix.clear();
   }

   void loop() {
       showPattern(HEART);
       showPattern(STAR);
       showPattern(SMILE);
       showPattern(ARROW);
       showPattern(CHECK);
   }

**The Patterns File (matrix_patterns.h)**

Before looking at how the sketch works, let's examine ``matrix_patterns.h`` — the separate header file where all five bitmap patterns are defined. Open it from the sketch's file list in App Lab:

.. code-block:: cpp
   :linenos:

   #ifndef MATRIX_PATTERNS_H
   #define MATRIX_PATTERNS_H

   #include <stdint.h>

   // 8 rows × 13 columns.
   // 1 = LED on, 0 = LED off.

   uint8_t HEART[8][13] = {
       {0,0,1,1,0,0,0,1,1,0,0,0,0},
       {0,1,1,1,1,0,1,1,1,1,0,0,0},
       {0,1,1,1,1,1,1,1,1,1,0,0,0},
       {0,0,1,1,1,1,1,1,1,0,0,0,0},
       {0,0,0,1,1,1,1,1,0,0,0,0,0},
       {0,0,0,0,1,1,1,0,0,0,0,0,0},
       {0,0,0,0,0,1,0,0,0,0,0,0,0},
       {0,0,0,0,0,0,0,0,0,0,0,0,0}
   };

   uint8_t STAR[8][13] = { /* ... 8 rows of 13 columns ... */ };
   uint8_t SMILE[8][13] = { /* ... 8 rows of 13 columns ... */ };
   uint8_t ARROW[8][13] = { /* ... 8 rows of 13 columns ... */ };
   uint8_t CHECK[8][13] = { /* ... 8 rows of 13 columns ... */ };

   #endif

Each pattern is a ``uint8_t[8][13]`` — a 2D array of 8 rows and 13 columns. A ``1`` lights the LED at that position; a ``0`` keeps it dark. The ``#ifndef`` / ``#define`` / ``#endif`` guards are standard C++ header boilerplate — they prevent the file from being included twice, which would cause duplicate-definition errors.

Now let's see how the sketch uses these patterns.

**How it Works**

The LED matrix is an 8×13 grid — 104 tiny LEDs arranged in rows and columns. Lighting them all at once would require 104 Arduino pins, which the board doesn't have. Instead, the matrix uses **multiplexing**: the control chip lights one row at a time, scanning through all 8 rows so fast (hundreds of times per second) that your eyes see a steady image. This is the same trick behind LED billboards, scoreboards, and digital clocks — your persistence of vision fills in the gaps.

The sketch itself is simple — the complexity lives in the library and the pattern data:

.. code-block:: text

   setup() → runs once at startup:
       Initialize the LED matrix hardware (Arduino_LED_Matrix library)
       Clear the display

   loop() → runs over and over forever:
       For each pattern name (HEART, STAR, SMILE, ARROW, CHECK):
           Pass it to showPattern()
           showPattern() calls renderBitmap() to light the right LEDs
           Wait DISPLAY_TIME (1000ms) so you can see it
       (repeat from HEART)

#. **Library Include and Matrix Object**

   - ``<Arduino_LED_Matrix.h>`` is the official Arduino library for the UNO R4 WiFi's built-in matrix — the UNO Q uses the same LED matrix hardware
   - ``matrix.begin()`` initializes the matrix controller chip and ``matrix.clear()`` blanks all LEDs so the display starts dark

   .. code-block:: arduino

      #include <Arduino_LED_Matrix.h>
      Arduino_LED_Matrix matrix;

      void setup() {
          matrix.begin();
          matrix.clear();
      }

#. **The showPattern() Helper**

   - ``renderBitmap(pattern, 8, 13)`` does the heavy lifting: it scans the 2D array, and for each row in sequence, it sets which of the 13 columns should be lit, then moves to the next row
   - The library handles the row-by-row multiplexing automatically — you just provide the bitmap data
   - ``DISPLAY_TIME`` is a named constant (1000 ms), making it easy to change the cycle speed in one place

   .. code-block:: arduino

      const unsigned long DISPLAY_TIME = 1000;

      void showPattern(uint8_t pattern[8][13]) {
          matrix.renderBitmap(pattern, 8, 13);
          delay(DISPLAY_TIME);
      }

#. **The 2D Array — A Grid of 1s and 0s**

   - Each inner array ``{0,0,1,1,0,...}`` is one row of 13 LEDs — reading left to right across the display
   - The outer array holds all 8 rows — reading top to bottom
   - Look at the HEART pattern: row 0 (top) has ``{0,0,1,1,0,0,0,1,1,0,0,0,0}`` — two lit clusters form the top lobes of the heart. Row 5 has ``{0,0,0,0,1,1,1,0,0,0,0,0,0}`` — three lit LEDs form the point at the bottom.
   - This is the same 2D array concept — each row is its own array, and the outer array holds them all together

   .. code-block:: arduino

      // HEART pattern — read row by row, top to bottom:
      uint8_t HEART[8][13] = {
          {0,0,1,1,0,0,0,1,1,0,0,0,0},  // row 0: top lobes
          {0,1,1,1,1,0,1,1,1,1,0,0,0},  // row 1
          // ... rows 2–6 ...
          {0,0,0,0,0,0,0,0,0,0,0,0,0}   // row 7: blank bottom margin
      };

#. **Separating Data from Logic**

   - Patterns live in ``matrix_patterns.h``, logic lives in ``sketch.ino`` — two separate files with distinct responsibilities
   - To add a new pattern, create a new 8×13 array in the header and add one ``showPattern()`` call to ``loop()`` — the sketch logic never changes
   - This separation is a fundamental software engineering principle: keep data and code apart so you can modify either independently

#. **How Multiplexing Works (You Don't Need to Code This)**

   The library handles it, but understanding the principle helps when debugging. Imagine you need to control 104 LEDs with only ~20 pins. The solution: light **one row at a time**, cycling through all 8 rows faster than the eye can see:

     Row 0 ON → Row 0 OFF, Row 1 ON → Row 1 OFF, Row 2 ON → ... → Row 7 ON → Row 7 OFF → repeat

   At any given instant, only 13 LEDs (one row) are actually lit. But because the scan happens hundreds of times per second, your persistence of vision blends them into a single steady image — the same reason a spinning fan looks like a blurry disc rather than individual blades.

3. Experiment
----------------

**Create a Custom Pattern**

Pick a new icon — a letter, a number, a simple shape — and create your own pattern. Draw it on graph paper first: 8 rows (top to bottom) and 13 columns (left to right). Then translate it to a new 2D array in ``matrix_patterns.h``:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Your Drawing
     - In the Array
   * - Filled square
     - ``1``
   * - Empty space
     - ``0``

Add your pattern to the cycle by adding one ``showPattern(yourPattern)`` call after the last existing one in ``loop()``.

**Challenge: Animate a Simple Icon**

Make an icon appear to move by showing it in one position, clearing the screen, then showing it shifted by one column. Use ``matrix.clear()`` between frames to prevent ghosting. Three frames of an arrow at different positions is enough to create the illusion of movement.

4. Troubleshooting
--------------------

**LED matrix doesn't light up at all**

* **Cause:** The USB cable is not connected, or the app didn't upload properly.
* **Solution:** Check the USB-C cable is firmly connected at both ends. Try clicking **Run** again — App Lab may have failed to upload silently.

**Only some LEDs light up**

* **Cause:** The bitmap dimensions passed to ``renderBitmap()`` don't match the array size.
* **Solution:** Make sure the second and third arguments are ``8`` and ``13`` — the exact size of the built-in matrix. Passing wrong dimensions will cause garbled output.

**Patterns look stretched or misaligned**

* **Cause:** The array dimensions are swapped — rows and columns reversed.
* **Solution:** Each inner array is a row (13 values), and the outer array holds 8 rows. If your pattern looks rotated or distorted, check that you have exactly 8 inner arrays with exactly 13 values each.

**App uploads but matrix stays dark**

* **Cause:** ``matrix.begin()`` wasn't called before ``renderBitmap()``.
* **Solution:** Verify that ``matrix.begin()`` is called in ``setup()`` before any rendering. Without initialization, the matrix hardware never activates.

5. Summary
-------------

You just turned 104 tiny LEDs into a programmable display! In this lesson, you learned:

* How to use the UNO Q's built-in LED matrix — no external components required
* How to define bitmap patterns as 2D arrays of 1s and 0s
* How to separate data (patterns) from logic (the sketch) using header files
* How ``renderBitmap()`` translates a grid of numbers into a visible image

In the next lesson, you'll turn the LED matrix into an interactive game — using buttons and patterns to test your reaction speed.
