.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

17 Opposite Reaction Game
=========================

Your UNO Q has been reading sensors and controlling outputs — now it's going to **play against you**. In this lesson, you'll build a reaction game: the LED matrix shows a left or right arrow at random, and you must press the **opposite** button to score. A correct answer earns a check mark and a happy chirp. A wrong answer shows an X and sounds a continuous alarm until you restart. It's your first program with game logic — random events, timed responses, and win/lose states.

In this lesson, you will learn to:

* Use ``random()`` to generate unpredictable game events
* Implement **game state logic** — setup, play, correct, wrong, restart
* Combine the LED matrix, buttons, and a passive buzzer into a single interactive system
* Use a simple software **debounce** to prevent a single press from registering multiple times

1. Setup
----------------------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * UNO Q
     - 1 * :ref:`cpn_breadboard`
     - 2 * :ref:`cpn_button`
     - 1 * Passive :ref:`cpn_buzzer`
   * - |list_pan_tilt|
     - |list_breadboard|
     - |list_button|
     - |list_passive_buzzer|
   * - Several :ref:`cpn_wires`
     - 1 * USB Cable
     -
     -
   * - |list_wire|
     - |list_usb_cable|
     -
     -

**Software Requirements**

This project uses no external libraries — the sketch only uses the built-in Arduino framework.

**Wiring Diagram**

Connect the left button to D7 and the right button to D6 — both use ``INPUT_PULLUP``, so do not add external pull-up or pull-down resistors — and the passive buzzer to D5; it has no polarity, so either pin can go to GND, while the built-in LED matrix needs no wiring.

.. image:: /img/wiring/wiring_buzzer_button.png
   :width: 500
   :align: center

2. Run the App
----------------

**Import and Run the Code**

#. Open **Arduino App Lab**, go to **Apps**. Click the dropdown arrow next to **Create new app +** and select **Import App**.

   .. image:: /img/app_import_app.png
      :width: 600

#. Select **Import from Computer**.

   .. image:: /img/app_import_pc.png
      :width: 600

#. Download :download:`17 Opposite Reaction Game.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/17.Opposite.Reaction.Game.zip>` and import it in App Lab. The app appears in **Apps** — click it to open.

#. Click the **Run** button (▶) in the top-right corner.

   .. image:: /img/app_run.png
      :width: 500

#. A smile appears on the LED matrix, then an arrow (left or right). Press the **opposite** button — left arrow → right button, right arrow → left button. A correct answer shows a check mark with a short beep and moves to the next round. A wrong answer shows an X with a continuous alarm. Press either button to restart.

**The Sketch (sketch.ino)**

Now that you've played the game, let's look at the sketch file.

.. code-block:: cpp
   :linenos:

   /*
    * Opposite Reaction Game
    *
    * Rules:
    * - When the matrix shows a LEFT arrow, press the RIGHT button.
    * - When the matrix shows a RIGHT arrow, press the LEFT button.
    * - A correct answer makes a short beep and starts the next round.
    * - A wrong answer shows an X and keeps the buzzer sounding.
    * - Press either button to restart after a wrong answer.
    */

   #include <Arduino_LED_Matrix.h>
   #include "matrix_patterns.h"

   const int LEFT_BUTTON_PIN = 7;
   const int RIGHT_BUTTON_PIN = 6;
   const int BUZZER_PIN = 5;

   const int CORRECT_TONE = 1200;
   const int WRONG_TONE = 350;

   Arduino_LED_Matrix matrix;

   enum Direction {
       LEFT,
       RIGHT
   };

   Direction currentArrow;
   bool gameOver = false;

   void showPattern(uint8_t pattern[8][13]) {
       matrix.renderBitmap(pattern, 8, 13);
   }

   void waitForButtonRelease() {
       while (digitalRead(LEFT_BUTTON_PIN) == LOW ||
              digitalRead(RIGHT_BUTTON_PIN) == LOW) {
           delay(10);
       }
       delay(50);
   }

   void startRound() {
       currentArrow = random(0, 2) == 0 ? LEFT : RIGHT;

       if (currentArrow == LEFT) {
           showPattern(LEFT_ARROW);
       } else {
           showPattern(RIGHT_ARROW);
       }
   }

   void correctAnswer() {
       showPattern(CHECK_MARK);

       tone(BUZZER_PIN, CORRECT_TONE);
       delay(120);
       noTone(BUZZER_PIN);

       delay(380);
       startRound();
   }

   void wrongAnswer() {
       gameOver = true;
       showPattern(CROSS_MARK);
       tone(BUZZER_PIN, WRONG_TONE);
   }

   void checkAnswer(Direction buttonPressed) {
       bool correct =
           (currentArrow == LEFT && buttonPressed == RIGHT) ||
           (currentArrow == RIGHT && buttonPressed == LEFT);

       if (correct) {
           correctAnswer();
       } else {
           wrongAnswer();
       }
   }

   void restartGame() {
       noTone(BUZZER_PIN);
       gameOver = false;

       showPattern(SMILE);
       delay(700);

       waitForButtonRelease();
       startRound();
   }

   void setup() {
       pinMode(LEFT_BUTTON_PIN, INPUT_PULLUP);
       pinMode(RIGHT_BUTTON_PIN, INPUT_PULLUP);
       pinMode(BUZZER_PIN, OUTPUT);

       matrix.begin();
       matrix.clear();

       randomSeed(micros());

       showPattern(SMILE);
       delay(1000);

       startRound();
   }

   void loop() {
       bool leftPressed = digitalRead(LEFT_BUTTON_PIN) == LOW;
       bool rightPressed = digitalRead(RIGHT_BUTTON_PIN) == LOW;

       if (gameOver) {
           if (leftPressed || rightPressed) {
               waitForButtonRelease();
               restartGame();
           }
           return;
       }

       if (leftPressed) {
           waitForButtonRelease();
           checkAnswer(LEFT);
       } else if (rightPressed) {
           waitForButtonRelease();
           checkAnswer(RIGHT);
       }
   }

**The Patterns File (matrix_patterns.h)**

This game uses five patterns, all defined in ``matrix_patterns.h`` — the same header-file approach used in the previous lesson:

.. code-block:: cpp

   uint8_t LEFT_ARROW[8][13] = {
       {0,0,0,0,0,0,0,0,0,0,0,0,0},
       {0,0,0,1,0,0,0,0,0,0,0,0,0},
       {0,0,1,1,0,0,0,0,0,0,0,0,0},
       {0,1,1,1,1,1,1,1,1,1,1,0,0},
       {0,0,1,1,0,0,0,0,0,0,0,0,0},
       {0,0,0,1,0,0,0,0,0,0,0,0,0},
       {0,0,0,0,0,0,0,0,0,0,0,0,0},
       {0,0,0,0,0,0,0,0,0,0,0,0,0}
   };

   uint8_t RIGHT_ARROW[8][13] = {
       {0,0,0,0,0,0,0,0,0,0,0,0,0},
       {0,0,0,0,0,0,0,0,0,1,0,0,0},
       {0,0,0,0,0,0,0,0,0,1,1,0,0},
       {0,1,1,1,1,1,1,1,1,1,1,1,0},
       {0,0,0,0,0,0,0,0,0,1,1,0,0},
       {0,0,0,0,0,0,0,0,0,1,0,0,0},
       {0,0,0,0,0,0,0,0,0,0,0,0,0},
       {0,0,0,0,0,0,0,0,0,0,0,0,0}
   };

   uint8_t CHECK_MARK[8][13] = {
       {0,0,0,0,0,0,0,0,0,0,0,0,0},
       {0,0,0,0,0,0,0,0,0,1,0,0,0},
       {0,0,0,0,0,0,0,0,1,1,0,0,0},
       {0,1,0,0,0,0,0,1,1,0,0,0,0},
       {0,1,1,0,0,0,1,1,0,0,0,0,0},
       {0,0,1,1,0,1,1,0,0,0,0,0,0},
       {0,0,0,1,1,1,0,0,0,0,0,0,0},
       {0,0,0,0,0,0,0,0,0,0,0,0,0}
   };

   uint8_t CROSS_MARK[8][13] = {
       {0,0,0,0,0,0,0,0,0,0,0,0,0},
       {0,0,1,0,0,0,0,0,1,0,0,0,0},
       {0,0,0,1,0,0,0,1,0,0,0,0,0},
       {0,0,0,0,1,0,1,0,0,0,0,0,0},
       {0,0,0,0,1,0,1,0,0,0,0,0,0},
       {0,0,0,1,0,0,0,1,0,0,0,0,0},
       {0,0,1,0,0,0,0,0,1,0,0,0,0},
       {0,0,0,0,0,0,0,0,0,0,0,0,0}
   };

   uint8_t SMILE[8][13] = { /* ... same 8×13 smile pattern from the LED matrix lesson ... */ };

Each pattern is drawn on the same 8×13 grid you used in the previous lesson. ``LEFT_ARROW`` points left (arrow head on the left, shaft to the right), ``RIGHT_ARROW`` points right. ``CHECK_MARK`` is a check mark, ``CROSS_MARK`` is an X, and ``SMILE`` is the welcome face.

**How it Works**

This lesson builds directly on LED matrix knowledge from the previous lesson — the patterns and rendering work the same way. What's new is the **game logic**: a state machine that reacts to button presses, evaluates the answer, and transitions between playing, correct, and game-over states:

.. code-block:: text

   setup() → runs once at startup:
       Initialize buttons (INPUT_PULLUP) and buzzer (OUTPUT)
       Initialize LED matrix, clear display
       Seed random generator with micros()
       Show SMILE for 1 second, then start first round

   loop() → runs over and over forever:
       Read both buttons (pressed = LOW because INPUT_PULLUP)
       Game over?
           Either button pressed? → waitForButtonRelease(), restartGame()
           Otherwise: return (skip — buzzer keeps sounding)
       Playing:
           Left pressed?  → waitForButtonRelease(), checkAnswer(LEFT)
           Right pressed? → waitForButtonRelease(), checkAnswer(RIGHT)

#. **The Direction Enum**

   - ``enum Direction { LEFT, RIGHT }`` gives meaningful names to the two possible arrow directions — ``LEFT`` and ``RIGHT`` are clearer than bare ``0`` and ``1``
   - ``currentArrow`` stores which arrow is currently displayed — it's used in ``checkAnswer()`` to compare against the button the player pressed
   - Using an enum is the same idea as naming a pin constant — ``LEFT`` says what it means; ``0`` doesn't

   .. code-block:: arduino

      enum Direction {
          LEFT,
          RIGHT
      };
      Direction currentArrow;

#. **Starting a Round — Did You Get LEFT or RIGHT?**

   - ``random(0, 2)`` returns either 0 or 1 — the two-argument form means "from 0 up to but not including 2"
   - ``randomSeed(micros())`` uses the microsecond timer as an unpredictable seed — every time you power up, the timer starts at a different value, so the arrow sequence is always different
   - ``if (currentArrow == LEFT)`` picks which pattern to display — ``LEFT_ARROW`` or ``RIGHT_ARROW`` — both defined in ``matrix_patterns.h``

   .. code-block:: arduino

      void startRound() {
          currentArrow = random(0, 2) == 0 ? LEFT : RIGHT;
          if (currentArrow == LEFT) {
              showPattern(LEFT_ARROW);
          } else {
              showPattern(RIGHT_ARROW);
          }
      }

#. **Checking the Answer — The Core Rule**

   - ``checkAnswer()`` evaluates the one rule of the game: the button pressed must be **opposite** to the arrow shown
   - ``(currentArrow == LEFT && buttonPressed == RIGHT)`` — left arrow, right button pressed = correct
   - ``(currentArrow == RIGHT && buttonPressed == LEFT)`` — right arrow, left button pressed = correct
   - Both conditions must be true for a correct answer — the ``||`` (OR) between them means "either case wins"

   .. code-block:: arduino

      void checkAnswer(Direction buttonPressed) {
          bool correct =
              (currentArrow == LEFT && buttonPressed == RIGHT) ||
              (currentArrow == RIGHT && buttonPressed == LEFT);

          if (correct) {
              correctAnswer();
          } else {
              wrongAnswer();
          }
      }

#. **Correct and Wrong — Two Different Outcomes**

   - ``correctAnswer()`` displays ``CHECK_MARK``, chirps at 1200 Hz for 120 ms with ``tone()`` / ``noTone()``, then waits 380 ms before starting the next round — the total 500 ms victory pause gives you time to see the check mark
   - ``wrongAnswer()`` sets ``gameOver = true``, displays ``CROSS_MARK``, and starts a continuous alarm — ``tone()`` runs forever because there's no ``noTone()`` and no ``delay()`` after it
   - Separating correct and wrong into their own functions keeps ``checkAnswer()`` clean — each outcome's details live in one place

   .. code-block:: arduino

      void correctAnswer() {
          showPattern(CHECK_MARK);
          tone(BUZZER_PIN, CORRECT_TONE);
          delay(120);
          noTone(BUZZER_PIN);
          delay(380);
          startRound();
      }

      void wrongAnswer() {
          gameOver = true;
          showPattern(CROSS_MARK);
          tone(BUZZER_PIN, WRONG_TONE);
      }

#. **Restarting After a Wrong Answer**

   - ``restartGame()`` stops the alarm (``noTone()``), clears the game-over flag, shows ``SMILE`` for 700 ms, then calls ``startRound()`` to begin a fresh round
   - ``waitForButtonRelease()`` is called **before** restarting — without it, the same button press that triggered the restart would immediately register as an answer in the new round
   - The 50 ms extra delay after release adds a small debounce buffer

   .. code-block:: arduino

      void restartGame() {
          noTone(BUZZER_PIN);
          gameOver = false;
          showPattern(SMILE);
          delay(700);
          waitForButtonRelease();
          startRound();
      }

#. **Debounce — One Press, One Action**

   - ``waitForButtonRelease()`` blocks (does nothing) until both buttons read ``HIGH`` (unpressed) — recall that ``INPUT_PULLUP`` means unpressed = ``HIGH``
   - Without this, a single finger press lasting 100 ms would trigger ``checkAnswer()`` ~10 times (at roughly 100 loop iterations per second) — the game would be unplayable
   - The 50 ms extra delay at the end catches any remaining contact bounce after the buttons go high

   .. code-block:: arduino

      void waitForButtonRelease() {
          while (digitalRead(LEFT_BUTTON_PIN) == LOW ||
                 digitalRead(RIGHT_BUTTON_PIN) == LOW) {
              delay(10);
          }
          delay(50);
      }

#. **The Two-Stage Loop — Game Over vs. Playing**

   - The first ``if (gameOver)`` check handles the alarm state — the continuous ``tone()`` keeps sounding, and the sketch does nothing else until a button restarts the game
   - The second part (playing normally) checks each button independently — ``if (leftPressed)`` / ``else if (rightPressed)`` — so only one button is processed per loop iteration
   - ``waitForButtonRelease()`` is called **before** ``checkAnswer()``, not after — this order means the release is handled first, then the answer is evaluated once

   .. code-block:: arduino

      void loop() {
          bool leftPressed = digitalRead(LEFT_BUTTON_PIN) == LOW;
          bool rightPressed = digitalRead(RIGHT_BUTTON_PIN) == LOW;

          if (gameOver) {
              if (leftPressed || rightPressed) {
                  waitForButtonRelease();
                  restartGame();
              }
              return;
          }

          if (leftPressed) {
              waitForButtonRelease();
              checkAnswer(LEFT);
          } else if (rightPressed) {
              waitForButtonRelease();
              checkAnswer(RIGHT);
          }
      }

3. Experiment
----------------

**Adjust the Game Difficulty**

Try changing the game parameters and observe how the feel changes:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Change
     - Effect on Gameplay
   * - Reduce the 1s welcome delay to 0.5s
     - Faster start — less time to prepare after upload
   * - Reduce the 500ms victory pause (120+380)
     - Faster rounds — the next arrow appears sooner
   * - Add a third button to D4
     - Three possible arrows — harder to react correctly
   * - Track and display score via Serial
     - Count correct answers before the first wrong one

**Challenge: Add a Score Counter**

Send the correct-streak count to the Serial Monitor. Reset it to zero on a wrong answer. How many correct answers can you get in a row?

.. dropdown:: Click to reveal solution
   :open:

   .. code-block:: cpp

      int streak = 0;  // Add at top of sketch

      // In correctAnswer(), before showPattern():
      streak++;
      Serial.print("Correct! Streak: ");
      Serial.println(streak);

      // In wrongAnswer(), before tone():
      Serial.print("Wrong! Final streak: ");
      Serial.println(streak);
      streak = 0;

   Add ``Serial.begin(115200)`` in ``setup()`` and open the Serial Monitor while playing. Compete with friends for the highest streak.

4. Troubleshooting
--------------------

**Buttons don't respond — game ignores presses**

* **Cause:** The buttons are wired incorrectly, or ``INPUT_PULLUP`` is not set.
* **Solution:** Check that the left button connects between D7 and GND, and the right button between D6 and GND. Verify ``pinMode(LEFT_BUTTON_PIN, INPUT_PULLUP)`` (D7) and ``pinMode(RIGHT_BUTTON_PIN, INPUT_PULLUP)`` (D6) are called in ``setup()``.

**Game registers multiple presses from a single click**

* **Cause:** The ``waitForButtonRelease()`` function isn't being called after each press.
* **Solution:** Make sure ``waitForButtonRelease()`` is called **before** ``checkAnswer()`` in ``loop()`` — the release must complete before evaluating the answer.

**Buzzer doesn't sound on correct or wrong answer**

* **Cause:** The buzzer pin is not connected, or the ``tone()`` function is using the wrong pin.
* **Solution:** Verify the passive buzzer is connected to D5 and both leads are firmly in the breadboard. Check that ``BUZZER_PIN`` is set to 5 in the code. Try a simple ``tone(5, 1000, 500)`` in ``setup()`` to test the buzzer independently.

**LED matrix shows garbled or no pattern**

* **Cause:** The pattern arrays in ``matrix_patterns.h`` are missing or have syntax errors.
* **Solution:** Make sure ``matrix_patterns.h`` is included at the top of the sketch and contains valid 8×13 arrays for all five patterns used: ``LEFT_ARROW``, ``RIGHT_ARROW``, ``CHECK_MARK``, ``CROSS_MARK``, and ``SMILE``. Check that each array has exactly 8 rows of 13 columns.

5. Summary
-------------

You just built a real game — random events, input handling, audio feedback, and game-over logic. In this lesson, you learned:

* How ``random()`` and ``randomSeed()`` create unpredictable events for games
* How to manage multiple game states with an ``enum`` and boolean flags
* How to combine the LED matrix, buttons, and a passive buzzer into a single interactive experience
* How a simple release-wait debounce prevents multiple inputs from a single press

In the next lesson, you'll use a PIR motion sensor — a sensor that can detect people — to build a motion-activated alarm. Everything you've learned here is a foundation for the IoT, AI, and multimedia projects ahead.
