.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

12 Thermistor-Controlled Fan
==============================

You've controlled a motor manually and sensed temperature digitally in earlier lessons. Now you'll connect the two to build an **automatic cooling system**: a temperature sensor that reads the room, and a fan that spins faster as it gets warmer — all without any human input. This is how your laptop's cooling fan, your car's radiator fan, and industrial temperature controllers work.

In this lesson, you will learn to:

* Read an **NTC thermistor** — an analog temperature sensor whose resistance changes with heat
* Convert an ``analogRead()`` voltage into a resistance, then into a temperature in °C
* Combine a temperature sensor with a DC motor to create a **closed-loop control system**
* Use ``math.h`` and the ``log()`` function for temperature calculation

1. Setup
----------------------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_thermistor`
     - 1 * :ref:`cpn_motor_xh254`
     - 1 * Fan Blade
   * - |list_pan_tilt|
     - |list_thermistor|
     - |list_motor|
     - |list_fan|
   * - 1 * :ref:`cpn_resistor` (10kΩ)
     - 1 * :ref:`cpn_breadboard`
     - Several :ref:`cpn_wires`
     - 1 * USB Cable
   * - |list_10kohm|
     - |list_breadboard|
     - |list_wire|
     - |list_usb_cable|

**Software Requirements**

This project uses no external libraries — the sketch only uses the built-in Arduino framework.

**Wiring Diagram**

Connect the motor to the Robot Shield's **M0** terminal (direction pin **D4**, PWM speed pin **D5**); place the thermistor — the small black bead with two leads, which has **no polarity** — between **A0** and GND, with the 10kΩ resistor (color bands Brown–Black–Orange–Gold) between **A0** and 3.3V; and avoid bending the thermistor's leads repeatedly at the body, as the bead is fragile.

.. image:: /img/wiring/wiring_thermistor_fan.png
   :width: 600
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


#. Navigate to the ``unoq-ai-kit/basic/`` folder and select ``12 Thermistor-Controlled Fan.zip``. The app appears in **Apps** — click it to open.

#. With the app open, click the **Run** button (▶) in the top-right corner.

   .. image:: /img/app_run.png
      :width: 500


#. Wait a few seconds for the upload to finish, then open the **Serial Monitor** (📊). You should see temperature readings and motor power levels. Gently pinch the thermistor bead between your fingers — the temperature should rise, and the fan should start spinning. Let go and watch it cool down and stop.

**The Sketch (sketch.ino)**

Now that you've seen the automatic cooling system respond to your body heat, let's look at the sketch file.

.. code-block:: cpp
   :linenos:

   /*
    * Reads an NTC thermistor and adjusts motor speed based on temperature.
    *
    * Thermistor: A0
    * Motor on the Robot Shield's M0 terminal:
    *   direction pin -> D4
    *   PWM pin       -> D5
    */

   #include <math.h>

   const int tempPin = A0;                  // Thermistor on analog pin A0
   const int motorDirPin = 4;               // Motor direction control
   const int motorPwmPin = 5;               // Motor speed control (PWM)

   // NTC thermistor parameters (Beta model)
   const float beta = 3950.0;              // Beta coefficient for this thermistor
   const float seriesResistor = 10000.0;   // 10k ohm fixed resistor
   const float nominalResistance = 10000.0; // Thermistor resistance at 25°C
   const float nominalTemp = 25.0 + 273.15; // 25°C in Kelvin

   void setup() {
       Serial.begin(115200);

       pinMode(motorDirPin, OUTPUT);
       pinMode(motorPwmPin, OUTPUT);
       digitalWrite(motorDirPin, HIGH);     // Fan blows forward
       analogWrite(motorPwmPin, 0);         // Motor starts OFF

       Serial.println("=== Temperature Controlled Motor ===");
   }

   void loop() {
       int adcValue = analogRead(tempPin);  // Read thermistor voltage (0–1023)

       // Step 1: Calculate thermistor resistance
       float resistance = (1023.0 / adcValue - 1.0) * seriesResistor;

       // Step 2: Convert resistance to temperature (Beta equation)
       float tempC = 1.0 / (log(resistance / nominalResistance) / beta
                      + 1.0 / nominalTemp) - 273.15;

       // Step 3: Map temperature to motor power
       int power;
       if (tempC < 25) {
           power = 0;                       // Below 25°C: fan OFF
       } else if (tempC > 50) {
           power = 100;                     // Above 50°C: fan at MAX
       } else {
           power = map((int)tempC, 25, 50, 20, 100);  // Smooth range
       }

       // Convert 0-100% to the 0-255 PWM range
       analogWrite(motorPwmPin, map(power, 0, 100, 0, 255));

       Serial.print("Temperature: ");
       Serial.print(tempC, 1);              // Print with 1 decimal place
       Serial.print(" *C    Motor Power: ");
       Serial.print(power);
       Serial.println("%");

       delay(500);
   }

**How it Works**

This lesson brings together analog sensing, mathematical conversion, and motor control into a single automatic system. The code has three stages: read → calculate → act:

.. code-block:: text

   setup() → runs once at startup:
       Start Serial Monitor
       Set motor direction pin D4 HIGH (fan blows forward)
       Set motor PWM pin D5 to 0 (fan starts off)
       Print startup message

   loop() → runs over and over forever:
       Read thermistor voltage on A0 (0–1023)
       Step 1: Convert ADC value → resistance (ohms)
       Step 2: Convert resistance → temperature (°C) using Beta equation
       Step 3: Convert temperature → motor power (0–100%)
       Convert power percentage → PWM value (0–255), write to D5
       Print temperature and power to Serial Monitor
       Wait 500ms, then repeat

1. **Library Include and Thermistor Constants**

   - The ``<math.h>`` library provides the ``log()`` function needed for the temperature calculation
   - ``beta`` (3950) describes how rapidly the thermistor's resistance changes with temperature
   - ``seriesResistor`` (10 kΩ) is the fixed resistor on the breadboard, and ``nominalResistance`` (10 kΩ) is the thermistor's resistance at 25°C

   .. code-block:: arduino

      #include <math.h>

      const float beta = 3950.0;
      const float seriesResistor = 10000.0;
      const float nominalResistance = 10000.0;
      const float nominalTemp = 25.0 + 273.15;

2. **Step 1: Converting the ADC Reading to Resistance**

   - The ADC reading (0–1023) comes from the voltage divider formed by the thermistor and the 10 kΩ fixed resistor
   - This formula reverses the voltage divider equation to recover the thermistor's resistance in ohms
   - If ``adcValue`` reads 512 (half of 1023), the thermistor resistance equals the series resistor — about 10 kΩ at room temperature

   .. code-block:: arduino

      int adcValue = analogRead(tempPin);
      float resistance = (1023.0 / adcValue - 1.0) * seriesResistor;

3. **Step 2: Converting Resistance to Temperature with the Beta Equation**

   - ``log()`` calculates the natural logarithm of the resistance ratio, and the Beta equation converts that into a temperature
   - The result is in Kelvin; subtracting 273.15 gives degrees Celsius
   - The key idea is simple: resistance goes in, and temperature in °C comes out — every thermistor-based thermometer uses this same math

   .. code-block:: arduino

      float tempC = 1.0 / (log(resistance / nominalResistance) / beta
                     + 1.0 / nominalTemp) - 273.15;

4. **Step 3: Mapping Temperature to Motor Power**

   - Three temperature zones control the fan: below 25°C the fan stays off, above 50°C it runs at maximum
   - Between 25°C and 50°C, ``map()`` scales the power smoothly — the warmer it gets, the faster the fan spins
   - This three-zone approach gives a natural feel: silent when cool, proportional response in the active range, and full blast when hot
   - The motor's **direction pin D4** was set ``HIGH`` in ``setup()`` so the fan blows forward; the **PWM pin D5** carries the speed

   .. code-block:: arduino

      if (tempC < 25) {
          power = 0;
      } else if (tempC > 50) {
          power = 100;
      } else {
          power = map((int)tempC, 25, 50, 20, 100);
      }

      analogWrite(motorPwmPin, map(power, 0, 100, 0, 255));

   - ``map(power, 0, 100, 0, 255)`` converts the percentage into the 0–255 range that ``analogWrite()`` uses — the same PWM speed control you used for the motor earlier

**Understanding the Thermistor Math (Simplified)**

If the formula seems complicated, here is the simplified version of what happens:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Step
     - What Happens
     - Formula (simplified)
   * - 1
     - Read the voltage at A0
     - ``analogRead(A0)`` → 0–1023
   * - 2
     - Calculate thermistor resistance from the voltage
     - ``R = 10kΩ × (1023 / reading − 1)``
   * - 3
     - Convert resistance to temperature using the Beta equation
     - ``T = 1 / (ln(R/10kΩ) / 3950 + 1/298.15) − 273.15``
   * - 4
     - Map temperature to motor power (25–50°C → 0–100%)
     - ``map(temp, 25, 50, 0, 100)``

Every NTC thermistor application follows these same four steps. The parameters (beta, nominal resistance, series resistor) change based on the specific components, but the pattern is universal.

3. Experiment
----------------

**Adjust the Temperature Thresholds**

Try changing the temperature range and observe how the fan responds:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Threshold Change
     - Effect
   * - ``25`` → ``20``, ``50`` → ``40``
     - Fan activates at a lower temperature — more aggressive cooling
   * - ``25`` → ``30``, ``50`` → ``60``
     - Fan activates at a higher temperature — lets the room get warmer before cooling
   * - ``if (tempC < 25) power = 0`` → ``power = 20``
     - Fan never fully stops — always runs at minimum 20% (like a PC's always-on fan)
   * - ``map((int)tempC, 25, 50, 0, 100)`` → ``map((int)tempC, 25, 50, 100, 0)``
     - Reversed: fan slows down as temperature rises (not useful, but shows how ``map()`` direction works)


**Challenge: Cold Mode — Heater Simulation**

Reverse the system: make the motor spin when the temperature is **below** a threshold (simulating a heater that turns on when it's cold). Map the motor speed so it's fastest at the coldest temperature.

.. dropdown:: Click to reveal solution
   :open:

   .. code-block:: cpp

      // Replace the power calculation in loop() with:
      int power;
      if (tempC > 35) {
          power = 0;                            // Warm → heater OFF
      } else if (tempC < 15) {
          power = 100;                          // Cold → heater at MAX
      } else {
          power = map((int)tempC, 15, 35, 100, 0);  // Colder = faster
      }

      // The map() output range is reversed (100 → 0):
      // tempC = 15 → power = 100 (coldest → fastest)
      // tempC = 35 → power = 0   (warmest → off)

   This inverts the system logic — same components, opposite behavior. Try breathing cold air on the thermistor (blow gently) to see the fan activate. This is how a thermostat-controlled heater works: the colder it gets, the harder it works.

4. Troubleshooting
--------------------

**Motor does not spin, even when the thermistor feels warm**

* **Cause:** The temperature isn't exceeding 25°C, or the thermistor circuit is wired incorrectly.
* **Solution:** Check the battery connection. Open the Serial Monitor — if the temperature reads below 25°C, pinch the thermistor firmly to warm it past the threshold. If the temperature reads 0°C or a negative number, check the voltage divider wiring: thermistor between GND and A0, 10kΩ resistor between A0 and 3.3V. Verify the motor is connected to the M0 terminal on the Robot Shield, with its direction wire on D4 and PWM wire on D5.

**Temperature readings are way off (0°C, 100°C, or negative)**

* **Cause:** The thermistor and resistor are swapped in the voltage divider, or the wrong resistor value is used.
* **Solution:** The thermistor should connect GND → A0, and the 10kΩ resistor should connect A0 → 3.3V. Swapping them inverts the voltage divider behavior. Double-check the resistor is 10kΩ (Brown-Black-Orange), not 220Ω (Red-Red-Brown).

**Temperature changes very slowly or not at all**

* **Cause:** The thermistor bead has high thermal mass, or the ``delay(500)`` is too short to see changes.
* **Solution:** The thermistor bead takes a few seconds to respond to temperature changes — it's not instant like a button. Pinch it firmly and wait 3–5 seconds for the reading to stabilize. The small bead size means it responds faster than a large sensor, but still not instantly.

**Motor runs at full speed regardless of temperature**

* **Cause:** The ``map()`` range doesn't match the actual temperature range, or the threshold logic is incorrect.
* **Solution:** Check the Serial Monitor for the actual temperature values. If room temperature is already reading above 50°C, there's a wiring or calculation error — see the previous troubleshooting item. If temperatures look correct, verify the ``if/else if`` thresholds are in the right order.


* **Cause:** The board is not connected, or App Lab can't find it.
* **Solution:** Check the USB-C cable is firmly connected at both ends. Try unplugging and re-plugging it. In App Lab, make sure your UNO Q is detected.

5. Summary
-------------

You've built a complete automatic control system — a sensor that reads the environment and an actuator that responds without any human intervention. In this lesson, you learned:

* How an NTC thermistor changes resistance with temperature — hotter → lower resistance
* How a voltage divider converts resistance into a voltage that ``analogRead()`` can measure
* How the Beta parameter equation converts resistance to temperature in °C using ``log()``
* How to combine sensor input with motor output to create a **closed-loop control system**
* How to set thresholds and use ``map()`` to create smooth, proportional responses

This is the same control loop used in server room cooling, 3D printer heated beds, and automotive engine management — sense, calculate, act. In the next lesson, you'll explore dual-axis analog input with a **joystick**, controlling servo position with intuitive, two-dimensional hand movements.
