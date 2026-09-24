.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

01 Hello LED
======================

Welcome to your first hardware lesson! In the Get Started section, you blinked the onboard LED on the UNO Q. Now you'll build a real circuit on a breadboard and control an external LED with code — the "Hello World" of electronics.

In this lesson, you will learn to:

* Build a circuit with an LED, resistor, and jumper wires on a breadboard
* Import and run an Arduino sketch in App Lab
* Use ``pinMode()`` and ``digitalWrite()`` to control an external LED
* Use ``delay()`` to create a blinking pattern

1. Setup
----------------------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_led`
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

**Software Requirements**

This project uses no external libraries — the sketch only uses the built-in Arduino framework.

**Wiring Diagram**

Connect the LED to **D5** through a 220Ω resistor: the long leg (anode) goes through the resistor to D5, and the short leg (cathode) to GND. Never connect an LED without a resistor — it burns out immediately.

.. image:: /img/wiring/wiring_led.png
   :width: 500
   :align: center

2. Run the App
----------------

**Import and Run the Code**

All code for this course is provided as ``.zip`` files that you can import directly into App Lab.

#. Download :download:`01 Hello LED.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/01.Hello.LED.zip>`.
#. In App Lab, go to **Apps** → **Create new app** → **Import App** → **Import from Computer**, and open the package you downloaded. The app appears in **Apps** — click it to open.

   .. image:: img/1_import_led.png
      :width: 600


#. With the app open, click the **Run** button (▶) in the top-right corner.

   .. image:: /img/app_run.png
      :width: 500


#. Wait a few seconds for the upload to finish, then check your breadboard — the LED should blink: half a second on, half a second off.


**The Sketch (sketch.ino)**

Now that you've seen the LED blink, let's look at the sketch file that makes it happen.

.. code-block:: cpp
   :linenos:

   /*
    * Blinks an external LED connected to pin 5.
    */

   const int ledPin = 5;  // LED connected to digital pin 5

   void setup() {
       pinMode(ledPin, OUTPUT);  // Set pin 5 as an output
   }

   void loop() {
       digitalWrite(ledPin, HIGH);  // Turn the LED on
       delay(500);                  // Wait half a second
       digitalWrite(ledPin, LOW);   // Turn the LED off
       delay(500);                  // Wait half a second
   }

**How it Works**

Every Arduino sketch has two functions, and this program follows a simple rhythm:

.. code-block:: text

   setup() → runs once at startup:
       Configure pin 5 as OUTPUT

   loop() → runs over and over forever:
       LED ON  → wait 500ms
       LED OFF → wait 500ms
       (repeat)

#. Pin Declaration and Setup

   - A constant ``ledPin`` stores the pin number, making it easy to change later
   - ``pinMode()`` configures the pin as an output since it sends voltage out to the LED
   - This only needs to run once at startup, so it goes in ``setup()``

   .. code-block:: arduino

      const int ledPin = 5;

      void setup() {
          pinMode(ledPin, OUTPUT);
      }

#. The Blink Loop

   - ``digitalWrite(ledPin, HIGH)`` sets the pin to 3.3V, allowing current to flow through the LED
   - ``delay(500)`` pauses the program for half a second, keeping the LED on
   - ``digitalWrite(ledPin, LOW)`` drops the pin to 0V, stopping the current and turning the LED off
   - Another ``delay(500)`` keeps it off before ``loop()`` runs from the top again

   .. code-block:: arduino

      void loop() {
          digitalWrite(ledPin, HIGH);
          delay(500);
          digitalWrite(ledPin, LOW);
          delay(500);
      }

3. Experiment
----------------

**Change the Blink Speed**

Try adjusting the ``delay()`` values and observe how the blink changes:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Delay Values
     - Effect
   * - ``delay(100)``
     - Fast flicker — 10 blinks per second
   * - ``delay(1000)``
     - Slow blink — once per second
   * - ON ``delay(100)``, OFF ``delay(900)``
     - Quick flash, long pause


**Challenge: SOS Signal**

SOS in Morse code is three short, three long, three short (··· −−− ···). Can you turn this into code?

.. dropdown:: Click to reveal solution
   :open:

   .. code-block:: cpp

      void loop() {
          // S: three dots
          for (int i = 0; i < 3; i++) {
              digitalWrite(ledPin, HIGH); delay(200);
              digitalWrite(ledPin, LOW);  delay(200);
          }
          delay(400);  // gap between letters

          // O: three dashes
          for (int i = 0; i < 3; i++) {
              digitalWrite(ledPin, HIGH); delay(600);
              digitalWrite(ledPin, LOW);  delay(200);
          }
          delay(400);

          // S: three dots
          for (int i = 0; i < 3; i++) {
              digitalWrite(ledPin, HIGH); delay(200);
              digitalWrite(ledPin, LOW);  delay(200);
          }
          delay(2000);  // pause before repeating
      }

4. Troubleshooting
--------------------

**LED does not light up**

* **Cause:** The LED is connected backwards, or a jumper wire is loose.
* **Solution:** Check that the long leg (anode) connects through the resistor to pin 5, and the short leg (cathode) connects to GND. Push all wires firmly into the breadboard.

**LED is very dim**

* **Cause:** Wrong resistor value.
* **Solution:** The 220Ω resistor is Red-Red-Brown-Gold. A 10kΩ resistor (Brown-Black-Orange) will make the LED barely visible. Use your Resistor Card to double-check.

**LED always on, never blinks**

* **Cause:** Code wasn't uploaded, or ``delay()`` values are too small.
* **Solution:** Make sure you clicked the **Run** button. If the delay is 1ms, the blink is too fast to see — try 500ms.

**LED was bright for a moment, then died**

* **Cause:** The LED was connected without a resistor and burned out.
* **Solution:** Replace the LED with a new one. Double-check that the 220Ω resistor is correctly in the circuit before running again.

5. Summary
-------------

Congratulations! You've built your first circuit and controlled it with code. In this lesson, you learned:

* How to wire an LED, a resistor, and jumper wires on a breadboard
* How to read a wiring diagram
* How to import and run a sketch in App Lab
* How ``pinMode()``, ``digitalWrite()``, and ``delay()`` work together
* That ``setup()`` runs once, and ``loop()`` runs forever

These four building blocks appear in every Arduino sketch you'll write from here on. In the next lesson, you'll add a button to control the LED — your first input device!
