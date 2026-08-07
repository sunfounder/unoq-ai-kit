.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

5. Web Game Interaction
===========================

Hardware isn't just for serious applications — it's for fun too. In this lesson, you'll use a physical button to control a character in a **browser-based game**. Press the button, and the character jumps over obstacles. The game logic runs in the browser (JavaScript), the button state flows through Python, and the hardware is just a single button — clean and responsive.

In this lesson, you will learn to:

* Stream button state from sketch → Python → browser in real time
* Build a simple game loop (gravity, collision, scoring) in JavaScript
* Handle responsive timing — button-to-jump latency under 100ms
* Separate concerns: hardware reads input, browser runs the game

1. Build the Circuit
----------------------

**Components Needed**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * :ref:`Arduino Uno Q <cpn_uno_q>`
     - 1 * :ref:`cpn_button`
     - Several :ref:`cpn_wires`
     -
   * - |list_uno_q|
     - |list_button|
     - |list_wire|
     -
   * - 1 * :ref:`cpn_breadboard`
     - 1 * USB Cable
     -
     -
   * - |list_breadboard|
     - |list_usb_cable|
     -
     -

**Wiring Diagram**

.. image:: img/5_web_game_fritzing.png
   :width: 700
   :align: center

Connect the button between **digital pin 2** and **GND** (uses ``INPUT_PULLUP``).

2. Code
----------

**Import the Code**

#. Go to **My Apps** → **Import App** → **Import from Computer**.

#. Navigate to ``unoq-ai-kit/iot/`` and select ``5_web_game.zip``. Open it.

**Run the Code**

#. Click **Run** (▶). A game window opens — a character on the left, obstacles scrolling from the right.

#. Press the physical button — the character jumps! Each cleared obstacle adds 1 point. Hit an obstacle and the game shows your score with a "Press button to restart" message.

.. image:: img/5_web_game_result.gif
   :width: 600
   :align: center

**The Code — sketch.ino**

Minimal — just reads the button and exposes it:

.. code-block:: cpp
   :linenos:

   #include <Arduino_RouterBridge.h>

   const int buttonPin = 2;
   bool lastButtonState = HIGH;

   void setup() {
       Monitor.begin();
       pinMode(buttonPin, INPUT_PULLUP);

       Bridge.begin();
       Bridge.provide("read_button", read_button);
   }

   void loop() {}

   bool read_button() {
       bool currentState = digitalRead(buttonPin);
       bool pressed = (lastButtonState == HIGH && currentState == LOW);
       lastButtonState = currentState;
       return pressed;
   }

.. note::

   ``read_button()`` returns ``true`` only on the **falling edge** — the transition from released (HIGH) to pressed (LOW). This ensures each press triggers exactly one jump, even if the button is held down.

**The Code — main.py**

Thin relay — polls the sketch and forwards button events:

.. code-block:: python
   :linenos:

   from arduino.app_utils import *
   from arduino.app_bricks.web_ui import WebUI
   import time

   ui = WebUI()

   def poll_button():
       while True:
           pressed = Bridge.call("read_button")
           if pressed:
               ui.send_message('button_pressed', {})
           time.sleep(0.02)  # Poll at ~50 Hz

   # Start polling in background
   import threading
   threading.Thread(target=poll_button, daemon=True).start()

   def on_get_initial_state(client, data):
       ui.send_message('game_ready', {}, client)

   ui.on_message('get_initial_state', on_get_initial_state)

   App.run()

**The Code — app.js (game logic)**

The game runs entirely in the browser:

.. code-block:: javascript

   // Game state
   let playerY = 250, velocity = 0, isJumping = false;
   let obstacleX = 700, score = 0, gameOver = false;
   const GROUND = 300, GRAVITY = 0.8, JUMP_FORCE = -14, SPEED = 6;

   const canvas = document.getElementById('game-canvas');
   const ctx = canvas.getContext('2d');

   socket.on('button_pressed', () => {
       if (!isJumping && !gameOver) {
           velocity = JUMP_FORCE;
           isJumping = true;
       }
       if (gameOver) restartGame();
   });

   function update() {
       if (!gameOver) {
           // Gravity
           if (isJumping) {
               playerY += velocity;
               velocity += GRAVITY;
               if (playerY >= GROUND) { playerY = GROUND; isJumping = false; }
           }
           // Move obstacle
           obstacleX -= SPEED;
           if (obstacleX < -30) { obstacleX = 700; score++; }
           // Collision
           if (obstacleX < 90 && obstacleX > 30 && playerY > GROUND - 50) {
               gameOver = true;
           }
       }
       draw();
       requestAnimationFrame(update);
   }

   update();

**How it Works**

.. mermaid::

   sequenceDiagram
       participant H as Button (Hardware)
       participant S as Sketch (sketch.ino)
       participant P as Python (main.py)
       participant B as Browser (Game)

       H->>S: Press button
       S->>S: falling edge detected
       S-->>P: read_button() -> true
       P-->>B: button_pressed
       B->>B: velocity = -14, player jumps!

The design decision: **game logic in the browser, not the sketch**. The sketch only reports "button pressed right now" (edge detection). Python polls at 50 Hz and forwards to the browser. The browser handles physics, rendering, collision, and scoring. This separation keeps the sketch simple and puts the complex logic where it's easiest to develop and debug.

3. Experiment
----------------

**Tune Game Difficulty**

In ``app.js``, adjust these constants:

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Parameter
     - Effect
   * - ``SPEED = 10``
     - Faster obstacles → harder
   * - ``GRAVITY = 1.0``
     - Heavier jump → falls faster
   * - ``JUMP_FORCE = -17``
     - Higher jump → more air time

**Challenge: Double Jump**

Allow a second jump while airborne. Track ``jumpCount`` — reset to 0 on landing, allow up to 2 jumps. In the ``button_pressed`` handler, check ``jumpCount < 2`` instead of ``!isJumping``.

**Challenge: Sound Effects**

Add an active buzzer to pin 5. Expose a ``play_beep(int duration)`` function. Call it from Python when the browser sends "scored" or "game_over" events:

.. code-block:: python

   ui.on_message('scored', lambda c,d: Bridge.call('play_beep', 100))
   ui.on_message('game_over', lambda c,d: Bridge.call('play_beep', 500))

4. Troubleshooting
--------------------

**Button press feels laggy**

* **Cause:** The 20ms polling interval adds up to 20ms latency, plus Bridge overhead.
* **Solution:** Polling at 50 Hz (20ms) plus ~5ms Bridge RPC gives ~25ms total latency — imperceptible. If it feels laggy, reduce ``time.sleep(0.02)`` to ``0.01``.

**One press triggers multiple jumps**

* **Cause:** ``read_button()`` returns the raw state instead of the falling edge.
* **Solution:** Make sure the sketch uses edge detection (``lastButtonState == HIGH && currentState == LOW``), not raw ``digitalRead()``. Raw reading would trigger a jump on every single poll while the button is held.

**Game runs too fast or too slow on different browsers**

* **Cause:** ``requestAnimationFrame`` adapts to the display refresh rate (60 Hz on most screens).
* **Solution:** Use **delta time** — multiply movement by the time elapsed since the last frame. This makes the game run at the same speed on 60 Hz, 120 Hz, or 144 Hz displays.

5. Summary
-------------

You built a game with a physical controller! In this lesson, you learned:

* How to poll a button at high frequency (50 Hz) through the Bridge
* How to use edge detection so each press triggers exactly one action
* How to run game logic entirely in the browser for maximum responsiveness
* How to send events from the browser back to Python for hardware feedback (sound)

In the next lesson, you'll build a professional climate dashboard with live-updating gauges, charts, and comfort indicators.
