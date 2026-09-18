.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

02 Button-Controlled Light
==========================

In the last lesson, you made an LED blink — but it just blinked on its own, following the code. Now you'll take control: press a button, the LED turns on. Release it, the LED turns off. This is your first step into **interactive** hardware — where the board reads input from the physical world and responds to you.

In this lesson, you will learn to:

* Read a button as a digital input using ``digitalRead()``
* Use ``INPUT_PULLUP`` to avoid floating pin problems
* Use ``if/else`` to make decisions based on input
* Combine input and output in a single program

1. Setup
----------------------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_button`
     - 1 * :ref:`cpn_led` (Red)
     - 1 * :ref:`cpn_resistor` (220Ω)
   * - |list_pan_tilt|
     - |list_button|
     - |list_red_led|
     - |list_220ohm|
   * - 1 * :ref:`cpn_breadboard`
     - Several :ref:`cpn_wires`
     - 1 * USB Cable
     -
   * - |list_breadboard|
     - |list_wire|
     - |list_usb_cable|
     -

**Software Requirements**

This project uses no external libraries — the sketch only uses the built-in Arduino framework.

**Wiring Diagram**

Connect the button to **D4** and the LED to **D5** through a 220Ω resistor (bands **Red → Red → Brown → Gold**): the button's two wires go to opposite sides of the center gap (one side to D4, the other to GND), and the LED's long leg (anode) goes to D5, short leg (cathode) to the resistor and GND.

.. image:: /img/wiring/wiring_button.png
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


#. Download :download:`02 Button-Controlled Light.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/02.Button-Controlled.Light.zip>` and import it in App Lab. The app appears in **Apps** — click it to open.

#. With the app open, click the **Run** button (▶) in the top-right corner.

   .. image:: /img/app_run.png
      :width: 500


#. Wait a few seconds for the upload to finish, then try pressing the button — the LED should light up while you hold it down, and turn off when you release it.

**The Sketch (sketch.ino)**

Now that you've seen the button control the LED, let's look at the sketch file that makes it happen.

.. code-block:: cpp
   :linenos:

   /*
    * Press the button to turn on the LED.
    */

   const int buttonPin = 4;  // Button connected to pin 4
   const int ledPin = 5;     // LED connected to pin 5

   void setup() {
       pinMode(buttonPin, INPUT_PULLUP);  // Pin 4 reads input with pull-up
       pinMode(ledPin, OUTPUT);           // Pin 5 controls the LED
   }

   void loop() {
       int buttonState = digitalRead(buttonPin);

       // Button pressed → LOW (connected to GND)
       if (buttonState == LOW) {
           digitalWrite(ledPin, HIGH);  // Turn LED ON
       } else {
           digitalWrite(ledPin, LOW);   // Turn LED OFF
       }
   }

**How it Works**

Every Arduino sketch follows the same rhythm, and this lesson introduces two new concepts — reading input and making decisions:

.. code-block:: text

   setup() → runs once at startup:
       Configure pin 4 as INPUT_PULLUP (button input, default HIGH)
       Configure pin 5 as OUTPUT (LED control)

   loop() → runs over and over forever:
       Read button state → is it pressed (LOW)?
           YES → turn LED ON
           NO  → turn LED OFF
       (repeat — checks the button thousands of times per second)

#. Setup — Configuring Input and Output

   - Two pins are declared: one for input (``buttonPin``) and one for output (``ledPin``)
   - ``INPUT_PULLUP`` enables the chip's built-in pull-up resistor, pulling the pin to 3.3V by default
   - When the button is pressed, the pin connects to GND and reads LOW — no external resistor needed

   .. code-block:: arduino

      const int buttonPin = 4;
      const int ledPin = 5;

      void setup() {
          pinMode(buttonPin, INPUT_PULLUP);
          pinMode(ledPin, OUTPUT);
      }

#. Loop — Reading the Button and Making Decisions

   - ``digitalRead()`` is the input version of ``digitalWrite()`` — it returns the pin's current state (HIGH or LOW) and stores it in a variable
   - The ``if/else`` statement lets the program make decisions based on conditions
   - The ``==`` operator checks equality: if ``buttonState`` equals ``LOW`` (button pressed), the LED turns on; otherwise it turns off

   .. code-block:: arduino

      void loop() {
          int buttonState = digitalRead(buttonPin);

          if (buttonState == LOW) {
              digitalWrite(ledPin, HIGH);
          } else {
              digitalWrite(ledPin, LOW);
          }
      }

#. Why ``INPUT_PULLUP`` Reads ``LOW`` When Pressed

   - The internal pull-up resistor weakly connects pin 4 to 3.3V, so it reads HIGH when nothing is connected
   - Pressing the button creates a direct path to GND (0V) — much stronger than the weak pull-up — so the voltage drops to LOW immediately
   - Without ``INPUT_PULLUP``, the pin would be "floating" when released, giving random HIGH/LOW readings

3. Experiment
----------------

**Swap the Logic**

What if you want the LED to be **on by default** and turn **off** when pressed? Swap the ``HIGH`` and ``LOW`` values inside the ``if/else`` block:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Logic
     - LED Behavior
   * - ``HIGH`` when pressed, ``LOW`` when released
     - LED lights up while button is held (default)
   * - ``LOW`` when pressed, ``HIGH`` when released
     - LED is on normally, turns off when button is pressed

To make this change:

.. code-block:: cpp

   if (buttonState == LOW) {
       digitalWrite(ledPin, LOW);   // LED OFF when pressed
   } else {
       digitalWrite(ledPin, HIGH);  // LED ON when released
   }


**Challenge: Toggle Switch**

What if you want the button to act like a toggle — press once to turn the LED on, press again to turn it off? This introduces a new concept: remembering state with a variable.

.. dropdown:: Click to reveal solution
   :open:

   .. code-block:: cpp

      const int buttonPin = 4;
      const int ledPin = 5;
      bool ledOn = false;            // Remember whether LED is on
      bool lastButtonState = HIGH;   // Previous button reading

      void setup() {
          pinMode(buttonPin, INPUT_PULLUP);
          pinMode(ledPin, OUTPUT);
      }

      void loop() {
          int reading = digitalRead(buttonPin);

          // Detect the moment the button is pressed (was HIGH, now LOW)
          if (lastButtonState == HIGH && reading == LOW) {
              ledOn = !ledOn;  // Flip the state: true → false, false → true
              digitalWrite(ledPin, ledOn ? HIGH : LOW);
              delay(50);       // Simple debounce
          }

          lastButtonState = reading;  // Remember for next loop
      }

   This pattern — detecting a **change** rather than the absolute state — is called **edge detection**. The ``!`` operator means "not": ``!true`` is ``false``, ``!false`` is ``true``. The ``? :`` is a compact if/else called the **ternary operator**.

4. Troubleshooting
--------------------

**LED does not light up when button is pressed**

* **Cause:** The button is plugged in the wrong orientation, or a jumper wire is loose.
* **Solution:** Buttons bridge across the center gap — pins on the same side are always connected. Make sure the two wires go to opposite sides of the button. Rotate the button 90° if needed. Push all wires firmly into the breadboard.

**LED stays on all the time, button does nothing**

* **Cause:** The pin mode might be set to ``INPUT`` instead of ``INPUT_PULLUP``.
* **Solution:** Without a pull-up, the pin floats and gives random readings. Use ``INPUT_PULLUP`` so the pin has a known default state (HIGH when released).

**LED behavior is reversed (on when released, off when pressed)**

* **Cause:** The ``HIGH`` and ``LOW`` are swapped in the ``if``/``else`` blocks, or the condition checks for ``HIGH`` instead of ``LOW``.
* **Solution:** With ``INPUT_PULLUP``, pressing the button gives ``LOW``. Check your ``if`` condition and the ``digitalWrite()`` values inside each block.

**Button works intermittently**

* **Cause:** Loose connection or breadboard wear.
* **Solution:** Push the button firmly into the breadboard. Check that jumper wires are fully inserted at both ends. Try a different row on the breadboard if the contacts feel loose.

5. Summary
-------------

Congratulations! You now know how to read input from the physical world. In this lesson, you learned:

* How to use ``digitalRead()`` to read a button's state
* How ``INPUT_PULLUP`` works and why it simplifies wiring
* How to use ``if/else`` to make decisions in code
* How one pin (input) can control another pin (output) — the foundation of interactive devices
* How to detect state **changes** with edge detection for toggle behavior

These input/output patterns appear in every interactive project you'll build. In the next lesson, you'll add a tilt switch and a buzzer to build a working alarm system.
