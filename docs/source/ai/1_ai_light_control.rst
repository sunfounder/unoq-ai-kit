.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

01 AI Light Control
======================

In every previous lesson, you told the hardware exactly what to do — ``digitalWrite(HIGH)``, ``setAngle(45)``, ``setRgb(1000, 0, 0)``. Now you'll talk to it like a person. Type *"make it sunset orange"* or *"turn off the light"*, and an LLM (large language model) translates your words into the correct RGB LED color.

In this lesson, you will learn to:

* Connect your UNO Q to OpenAI's GPT-4o-mini via the **CloudLLM** brick
* Configure an API key in App Lab
* Write a **system prompt** that constrains the LLM to only output valid color names
* Use Bridge to pass AI decisions from Python to the Arduino sketch

1. Build the Circuit
----------------------

**Components Needed**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * :ref:`Arduino Uno Q <cpn_uno_q>`
     - 1 * Robot Shield
     - 1 * :ref:`cpn_rgb_led` (Common Cathode)
     - 3 * :ref:`cpn_resistor` (220Ω)
   * - |list_uno_q|
     - |list_robot_shield|
     - |list_rgb_led|
     - |list_220ohm|
   * - 1 * :ref:`cpn_breadboard`
     - Several :ref:`cpn_wires`
     - 1 * USB Cable
     -
   * - |list_breadboard|
     - |list_wire|
     - |list_usb_cable|
     -

.. tip::

   You'll need an **OpenAI API Key** for this lesson. App Lab will prompt you to enter it when you first click Run. The key is stored securely and only used for LLM requests from your board.

**Wiring Diagram**

Follow the diagram below to connect the RGB LED to the Robot Shield's PWM channels.

.. image:: img/wiring_rgb_led.png
   :width: 500
   :align: center

.. warning::

   The RGB LED's **longest leg is the common cathode** — connect it to GND. Each of the three shorter legs goes to a separate PWM channel through a 220Ω resistor. Never connect an RGB LED pin directly without a resistor.

**Circuit Diagram**

The schematic below shows the same circuit in electrical notation.

.. image:: img/sche_rgb_led.png
   :width: 500
   :align: center

Each color channel gets independent PWM control:

  **Red anode → 220Ω → P6**

  **Green anode → 220Ω → P5**

  **Blue anode → 220Ω → P4**

  **Common cathode → GND**

2. Code
----------

**Import and Run the Code**

All code for this course is provided as ``.zip`` files that you can import directly into App Lab.

#. Open **Arduino App Lab**, go to **My Apps**. Click the dropdown arrow next to **Create new app +** and select **Import App**.

   .. image:: img/app_import_app.png
      :width: 600
      :align: center

#. Select **Import from Computer**.

   .. image:: img/app_import_pc.png
      :width: 600
      :align: center

#. Navigate to the ``unoq-ai-kit/ai/`` folder and select ``01 AI Light Control.zip``. The app appears in **My Apps** — click it to open.

#. Click the **Run** button (▶). App Lab will ask for your **OpenAI API Key**. Enter it and click Save, then click Run again.

#. When the Web UI opens, type a command like *"Turn the light red"* and press Send. The RGB LED changes color and the chat responds.

**How it Works**

.. mermaid::

   sequenceDiagram
       participant B as Browser (chat input)
       participant P as Python (main.py)
       participant L as OpenAI GPT-4o-mini
       participant S as Sketch (sketch.ino)

       B->>P: socket.emit("command", {text: "make it blue"})
       P->>L: CloudLLM.chat_stream("make it blue")
       L-->>P: "blue"
       P->>S: Bridge.call("set_color", 3)
       S->>S: setRgb(0, 0, 1000)
       P-->>B: {text: "Light set to blue", color: "blue"}

**Python (main.py)** — runs on the Linux MPU

  * ``WebUI()`` serves the chat interface from the assets folder
  * ``CloudLLM(model="openai:gpt-4o-mini")`` connects to OpenAI
  * The **system prompt** tells the LLM to only respond with color names
  * ``llm.chat_stream(message)`` sends the user's words and gets a one-word response
  * ``Bridge.call("set_color", code)`` sends the color as an integer code to the sketch
  * ``ui.send_message("response", ...)`` sends the reply back to the browser

**Sketch (sketch.ino)** — runs on the STM32 MCU

  * ``Bridge.provide("set_color", set_color)`` registers the function Python can call
  * ``set_color(int code)`` translates the code into RGB PWM values via a switch statement
  * Three ``Pwm`` objects on P6 (R), P5 (G), P4 (B) control the LED channels
  * ``setRgb(r, g, b)`` writes all three pulse widths at once

**The System Prompt**

The system prompt is the key to making the LLM behave reliably. Here's what this lesson uses:

.. code-block:: text

   You are an AI assistant controlling an RGB LED.

   Supported colors:
   red
   green
   blue
   yellow
   white

   If the user wants to turn off the light, reply with:

   off

   Reply with ONLY ONE WORD.

This prompt constrains the LLM to only respond with valid color names. Without it, the LLM might respond with a full sentence like "Sure, I'll make the light blue for you!" — which the code can't parse. The prompt ensures the output is always exactly one word.

3. Experiment
----------------

**Try Different Phrasings**

The LLM understands natural language — you don't need to use exact commands. Try different ways of asking for the same color:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Your Words
     - LLM Responds
   * - "Turn the light red"
     - red
   * - "I want it to be blue"
     - blue
   * - "Make it green please"
     - green
   * - "Switch off"
     - off
   * - "Give me yellow"
     - yellow

**Challenge: What Happens with Unknown Colors?**

Try asking for a color that isn't in the list, like *"make it purple"* or *"set it to orange"*. What happens? The LLM might still guess a close match, or the code might reject it. This shows the importance of the system prompt — it defines the boundaries of what the LLM can control.

**Challenge: Break the System**

Try these tricky inputs and see how the LLM handles them:

* *"What's the weather like?"* — unrelated question
* *"Don't turn the light red"* — negation, does it still say "red"?
* *"I want the light to be the color of the sky"* — abstract concept

Each failure case teaches you something about prompt engineering — how to write prompts that make LLMs behave predictably.

4. Troubleshooting
--------------------

**"Please configure your API Key" message**

* **Cause:** The OpenAI API key hasn't been entered, or is invalid.
* **Solution:** Click Run — App Lab will prompt for the key. If you already entered it, check that it's valid at platform.openai.com/api-keys.

**LLM responds but RGB LED doesn't change**

* **Cause:** The LLM returned a color that isn't supported, or Bridge communication failed.
* **Solution:** Check the Web UI chat — it shows what the LLM returned. If it's a valid color like "red" but the LED didn't change, check the RGB LED wiring and the Robot Shield connection.

**RGB LED shows wrong color (e.g., red looks purple)**

* **Cause:** The PWM channel mapping doesn't match your wiring.
* **Solution:** Verify that the red anode goes to P6, green to P5, and blue to P4. If colors are still off, try swapping the PWM pin numbers in the sketch.

**Web UI doesn't open**

* **Cause:** The app isn't running, or the browser can't connect.
* **Solution:** Make sure you clicked **Run** in App Lab. Check that the Web UI tab opened — if a popup was blocked, allow popups for App Lab.

5. Summary
-------------

You've connected an AI language model to physical hardware! In this lesson, you learned:

* How to use the CloudLLM brick to send messages to OpenAI's GPT
* How a system prompt constrains the LLM to output predictable, machine-readable responses
* How Bridge passes AI decisions from Python to the Arduino sketch
* How natural language can replace hardcoded commands for hardware control

**AI converts natural language into hardware commands.**

In the next lesson, you'll use the LLM to control servos — telling the UNO Q to pan left, tilt up, or center itself, all with natural language.
