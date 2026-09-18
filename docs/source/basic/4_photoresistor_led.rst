.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

04 Photoresistor Night Light
==============================

In the first three lessons, every signal was either ON or OFF — button pressed or not, tilt detected or not, LED lit or dark. Now you'll enter the world of **analog** signals, where values can vary smoothly across a continuous range. A **photoresistor** (light-dependent resistor) changes its resistance with light, producing a voltage that the UNO Q can measure. The brighter the light, the more LEDs turn on — like a visual light meter. This is your first **analog sensor**.

In this lesson, you will learn to:

* Read a photoresistor as an analog light sensor
* Use **arrays** to manage multiple pins with clean, compact code
* Use ``for`` loops to repeat actions across a group of components
* Build a 4-level LED bar graph that responds to ambient light

1. Setup
----------------------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_photoresistor`
     - 4 * :ref:`cpn_led`
     - 4 * :ref:`cpn_resistor` (220Ω)
   * - |list_pan_tilt|
     - |list_photoresistor|
     - |list_red_led|
     - |list_220ohm|
   * - 1 * :ref:`cpn_breadboard`
     - Several :ref:`cpn_wires`
     - 1 * USB Cable
     - 1 * :ref:`cpn_resistor` (10kΩ)
   * - |list_breadboard|
     - |list_wire|
     - |list_usb_cable|
     - |list_10kohm|

**Software Requirements**

This project uses no external libraries — the sketch only uses the built-in Arduino framework.

**Wiring Diagram**

Connect the photoresistor between **3.3V** and **A0** — it has no polarity, so either leg works — and the **10kΩ fixed resistor** (bands **Brown → Black → Orange**) between **A0** and **GND**; the two resistors form a voltage divider that turns light into a readable voltage. The four LEDs go to **D4, D5, D6, D7**, each with its **own** 220Ω resistor (bands **Red → Red → Brown → Gold**) and a shared GND rail: the long leg (anode) goes toward the digital pin, the short leg (cathode) toward GND. Never connect multiple LEDs to a single resistor — they share current unevenly and may burn out.

.. image:: /img/wiring/wiring_photoresistor_led.png
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


#. Download :download:`04 Photoresistor Night Light.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/04.Photoresistor.Night.Light.zip>` and import it in App Lab. The app appears in **Apps** — click it to open.

#. With the app open, click the **Run** button (▶) in the top-right corner.

   .. image:: /img/app_run.png
      :width: 500


#. Wait a few seconds for the upload to finish, then try shining a flashlight on the photoresistor — all 4 LEDs should light up. Cover it with your hand — the LEDs should dim. Open the Serial Monitor (📊) to see the live light readings.

#. Switch to the **Serial Monitor** window to view the current output.


   .. image:: img/04_open_serial.png

**The Sketch (sketch.ino)**

Now that you've seen the circuit respond to light, let's look at the sketch file.

.. code-block:: cpp
   :linenos:

   /*
    * A 4-level LED bar graph that responds to ambient light.
    */

   const int lightPin = A0;               // Photoresistor on analog pin A0
   const int ledPins[] = {4, 5, 6, 7};   // LEDs on digital pins D4–D7

   void setup() {
       Serial.begin(115200);

       // Initialize all 4 LEDs at once with a for loop
       for (int i = 0; i < 4; i++) {
           pinMode(ledPins[i], OUTPUT);
           digitalWrite(ledPins[i], LOW);
       }

       Serial.println("=== Light Sensor LED Indicator ===");
   }

   void loop() {
       int lightValue = analogRead(lightPin);           // Read light sensor (0–1023)
       int level = map(lightValue, 0, 1023, 1, 4);      // Divide into 4 brightness levels

       // Update each LED: ON if below the level threshold, OFF otherwise
       for (int i = 0; i < 4; i++) {
           digitalWrite(ledPins[i], (i < level) ? HIGH : LOW);
       }

       Serial.print("Light: ");
       Serial.print(lightValue);
       Serial.print("  Level: ");
       Serial.println(level);

       delay(100);
   }

**How it Works**

This lesson introduces two powerful programming tools — arrays and ``for`` loops — that let you control groups of pins with just a few lines of code:

.. code-block:: text

   setup() → runs once at startup:
       Start Serial Monitor
       For each LED (0 to 3):
           Set pin as OUTPUT, turn it OFF
       Print startup message

   loop() → runs over and over forever:
       Read photoresistor on A0 (0–1023)
       Map light value to 4 levels (1–4)
       For each LED (0 to 3):
           If its position < level → ON
           Otherwise → OFF
       Print values to Serial Monitor
       Wait 100ms, then repeat

#. Storing Multiple Pins in an Array

   - An **array** is a single variable that stores multiple values instead of declaring separate variables for each pin
   - Arrays use zero-based indexing: ``ledPins[0]`` is pin 4, ``ledPins[1]`` is pin 5, and so on
   - This structure lets you loop through every pin automatically

   .. code-block:: arduino

      const int ledPins[] = {4, 5, 6, 7};

#. Reading an Analog Sensor and Mapping to Levels

   - ``analogRead()`` reads the voltage on pin A0 and returns a number from 0 to 1023
   - The ``map()`` function rescales the wide 0–1023 range down to just four levels (1 through 4)
   - A bright room reading near 1023 becomes level 4 (four LEDs on); a dark reading near 0 becomes level 1 (one LED on)

   .. code-block:: arduino

      int lightValue = analogRead(lightPin);
      int level = map(lightValue, 0, 1023, 1, 4);

#. Controlling All LEDs with a For Loop

   - The ``for`` loop runs four times, once for each LED, with counter ``i`` going from 0 to 3
   - ``ledPins[i]`` refers to the pin number for that position in the array
   - The **ternary operator** ``(i < level) ? HIGH : LOW`` checks if the LED's index is below the current level and turns it on if so, off otherwise

   .. code-block:: arduino

      for (int i = 0; i < 4; i++) {
          digitalWrite(ledPins[i], (i < level) ? HIGH : LOW);
      }

**Why an Array + Loop Is Better**

Without arrays or loops, controlling four LEDs would take many repetitive lines:

.. code-block:: arduino

   pinMode(4, OUTPUT); digitalWrite(4, LOW);
   pinMode(5, OUTPUT); digitalWrite(5, LOW);
   pinMode(6, OUTPUT); digitalWrite(6, LOW);
   pinMode(7, OUTPUT); digitalWrite(7, LOW);

With an array and a loop, the same work is done in just three lines inside ``loop()``. If you later add a fifth LED, you change one number (``4`` to ``5``) and add one pin to the array — the loop handles everything automatically. This pattern scales to dozens of components.

3. Experiment
----------------

**Change the Bar Graph Direction**

Try making the bar graph fill in the opposite direction — more LEDs on in bright light, fewer in dark:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Change
     - How
   * - Reverse the level mapping
     - ``map(lightValue, 0, 1023, 4, 1)`` — dark → 4 LEDs, bright → 1 LED
   * - Reverse the fill direction
     - ``(i >= (4 - level)) ? HIGH : LOW`` — LEDs fill from right to left
   * - Both
     - Dark fills from right, bright fills from left — a completely different feel

For each change, one line in ``loop()`` is all you need to modify. The array and loop handle the rest.

**Challenge: Night Light with a Twist**

A real night light should turn **off** during the day and only activate at night. Add a threshold: when ``lightValue`` is above 700 (bright), all LEDs stay off regardless. When below 700 (dim/dark), the bar graph activates normally.

.. dropdown:: Click to reveal solution
   :open:

   .. code-block:: cpp

      void loop() {
          int lightValue = analogRead(lightPin);

          if (lightValue > 700) {
              // Daytime: all LEDs off to save power
              for (int i = 0; i < 4; i++) {
                  digitalWrite(ledPins[i], LOW);
              }
          } else {
              // Nighttime: bar graph active
              int level = map(lightValue, 0, 700, 1, 4);
              for (int i = 0; i < 4; i++) {
                  digitalWrite(ledPins[i], (i < level) ? HIGH : LOW);
              }
          }

          Serial.print("Light: ");
          Serial.println(lightValue);

          delay(100);
      }

   Notice how the ``map()`` input range changed from ``0, 1023`` to ``0, 700`` — this remaps only the nighttime values (0–700) across all 4 levels, giving you full resolution in the range that matters. This is a common technique: adapt your sensor's working range to the conditions you care about.

4. Troubleshooting
--------------------

**Only 1 LED lights up, or no LEDs in a dim room**

* **Cause:** This is expected behavior — with the photoresistor connected to 3.3V, bright light produces a higher ``analogRead()`` value and lights more LEDs. In a dark room, the reading is low and fewer LEDs turn on.
* **Solution:** Shine a flashlight directly on the photoresistor — all 4 LEDs should light up. If you want the opposite behavior (dark → more LEDs, like a real night light), swap the photoresistor and fixed resistor: connect the photoresistor between A0 and GND, and the fixed resistor between 3.3V and A0.

**All 4 LEDs stay on all the time**

* **Cause:** The photoresistor circuit has a short or the wrong resistor is installed, always reading maximum value.
* **Solution:** Check that the fixed resistor from A0 to GND is installed (usually 10kΩ — Brown-Black-Orange). Without it, A0 floats near 3.3V and always reads high. Also check for loose jumper wires.

**Some LEDs never turn on**

* **Cause:** A specific LED is burned out, connected backwards, or on the wrong breadboard row.
* **Solution:** Swap the suspect LED with a known working one to test. Check polarity — the long leg goes toward the digital pin. Verify the jumper wire from the digital pin to the LED's row is fully inserted.

5. Summary
-------------

Congratulations! Your circuit now senses the world on its own — no knobs, no buttons, just automatic response to light. In this lesson, you learned:

* How a photoresistor changes resistance with light, and how to read it with ``analogRead()``
* How **arrays** store multiple related values in a single, elegant variable
* How ``for`` loops repeat code across every element of an array — write once, run many times
* How the **ternary operator** (``? :``) makes simple decisions compact
* How to reuse ``map()`` in a new context — adapting sensor ranges to your application

Arrays and loops are fundamental programming patterns you'll use in nearly every future lesson. In the next lesson, you'll meet a new kind of sensor — a PIR motion sensor that detects movement and triggers a buzzer alarm.
