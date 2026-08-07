.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

4. AI Gesture Control
=========================

What if you could control hardware without touching anything — just by moving your hand? In this lesson, you'll use the camera to recognize **hand gestures** and map them to commands: thumbs up turns on an LED, open palm turns it off, a fist makes it blink. Your hand becomes a remote control.

In this lesson, you will learn to:

* Run a gesture recognition model on the camera feed
* Map different gestures to different hardware actions
* Control an LED and buzzer with hand signals
* Understand how gesture classification differs from object detection

1. Build the Circuit
----------------------

**Components Needed**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * :ref:`Arduino Uno Q <cpn_uno_q>`
     - 1 * Multimedia Carrier
     - 1 * Camera Module
     - 1 * :ref:`cpn_led` (Red)
   * - |list_uno_q|
     - |list_uno_q|
     - |list_uno_q|
     - |list_red_led|
   * - 1 * :ref:`cpn_resistor` (220Ω)
     - 1 * :ref:`cpn_buzzer`
     - Several :ref:`cpn_wires`
     - 1 * :ref:`cpn_breadboard`
   * - |list_220ohm|
     - |list_active_buzzer|
     - |list_wire|
     - |list_breadboard|

**Wiring Diagram**

.. image:: img/4_gesture_fritzing.png
   :width: 700
   :align: center

Here are the connections to make:

#. Connect the red LED (with 220Ω resistor) between **digital pin 5** and **GND** — same circuit as Lesson 1.

#. Connect the active buzzer: **VCC** to **digital pin 6**, **GND** to any **GND** pin.

#. Make sure the camera is mounted on the Multimedia Carrier and pointed toward where you'll make gestures — about 30–50 cm away works best.

2. Code
----------

**Import the Code**

#. In App Lab, go to **My Apps** → **Import App** → **Import from Computer**.

#. Navigate to ``unoq-ai-kit/edge_ai/`` and select ``4_ai_gesture_control.zip``.

#. Open the imported app.

**Run the Code**

#. Click the **Run** button (▶).

#. Hold your hand about 30–50 cm from the camera, with your palm facing the lens.

#. Try these gestures and watch the hardware respond:

   * **Open palm** → LED on, buzzer silent
   * **Closed fist** → LED off, buzzer silent
   * **Thumbs up** → LED blinks, buzzer beeps once

.. image:: img/4_gesture_result.gif
   :width: 600
   :align: center

**The Code**

.. code-block:: cpp
   :linenos:

   /*
    * Lesson 4: AI Gesture Control
    * Recognizes hand gestures and controls LED + buzzer.
    */

   #include <Arduino_RouterBridge.h>
   #include "camera.h"
   #include "edge_impulse.h"

   const int ledPin = 5;
   const int buzzerPin = 6;

   String lastGesture = "";

   void setup() {
       Monitor.begin();
       Camera.begin();
       AI.begin("gesture_recognition.eim");

       pinMode(ledPin, OUTPUT);
       pinMode(buzzerPin, OUTPUT);
   }

   void loop() {
       Camera.capture();
       AIResult result = AI.classify();

       if (result.detected) {
           String gesture = result.label;

           // Only act when the gesture changes
           if (gesture != lastGesture) {
               lastGesture = gesture;
               Monitor.print("Gesture: ");
               Monitor.println(gesture);

               if (gesture == "open_palm") {
                   digitalWrite(ledPin, HIGH);   // LED ON
                   digitalWrite(buzzerPin, LOW);
               }
               else if (gesture == "fist") {
                   digitalWrite(ledPin, LOW);    // LED OFF
                   digitalWrite(buzzerPin, LOW);
               }
               else if (gesture == "thumbs_up") {
                   // Blink LED and beep
                   digitalWrite(ledPin, HIGH);
                   digitalWrite(buzzerPin, HIGH);
                   delay(200);
                   digitalWrite(ledPin, LOW);
                   digitalWrite(buzzerPin, LOW);
               }
           }
       }
   }

**How it Works**

.. code-block:: text

   setup() → runs once:
       Initialize camera + gesture model
       Configure LED and buzzer pins

   loop() → runs forever:
       Capture frame → classify gesture
       Gesture detected?
           YES → is it different from last gesture?
               YES → run the matching action
                   open_palm → LED ON
                   fist      → LED OFF
                   thumbs_up → LED blink + beep
           Store current gesture for next comparison

Here's what's new in this lesson:

* **Gesture classification** — Unlike object detection (which finds objects AND their locations), this model classifies the entire frame as one of several gesture types. The whole image gets one label: "open_palm", "fist", or "thumbs_up".
* **Change detection** — The code only acts when the gesture **changes** (``gesture != lastGesture``). Without this, the LED would continuously blink on every loop iteration while the same gesture is held — potentially thousands of times per second. Change detection makes the system respond once per new gesture.
* **Gesture-to-action mapping** — A clear ``if / else if`` chain maps each recognized gesture to a specific hardware action. This pattern scales easily: add a new gesture by adding another ``else if`` branch.

3. Experiment
----------------

**Add More Gestures**

If your model supports additional gestures (pointing finger, peace sign, etc.), add them to the mapping chain with new hardware behaviors. For example:

* **Pointing finger** → servo turns to a specific angle
* **Peace sign** → play a short melody on the buzzer

**Challenge: Gesture Lock**

Create a gesture-based "lock": require the user to show **thumbs up → fist → open palm** in sequence to unlock. Track the sequence with a counter that resets on wrong gestures.

.. dropdown:: Click to reveal approach

   .. code-block:: cpp

      int sequenceStep = 0;

      void loop() {
          // ... capture and classify ...
          if (gesture != lastGesture) {
              if (sequenceStep == 0 && gesture == "thumbs_up") sequenceStep = 1;
              else if (sequenceStep == 1 && gesture == "fist") sequenceStep = 2;
              else if (sequenceStep == 2 && gesture == "open_palm") {
                  Monitor.println("Unlocked!");
                  digitalWrite(ledPin, HIGH);
                  sequenceStep = 0;
              } else {
                  sequenceStep = 0;  // Wrong gesture, reset
              }
          }
      }

4. Troubleshooting
--------------------

**Gesture is never recognized, or always "unknown"**

* **Cause:** Hand is too close, too far, or not well-lit.
* **Solution:** Hold your hand 30–50 cm from the camera with your palm facing the lens. Make sure the room is well-lit and your hand is against a plain background. Avoid busy backgrounds that confuse the model.

**Same gesture triggers repeatedly**

* **Cause:** The change detection logic is missing or not working.
* **Solution:** Make sure ``lastGesture = gesture;`` is inside the ``if (gesture != lastGesture)`` block. If it's outside, ``lastGesture`` gets updated even when the gesture hasn't changed, breaking the comparison.

**Thumbs up is confused with fist**

* **Cause:** The model has difficulty distinguishing these gestures at certain angles.
* **Solution:** Hold your hand with the thumb clearly extended to the side, perpendicular to your fingers. Make sure the thumb is fully visible and not obscured by other fingers.

**LED reacts but buzzer doesn't**

* **Cause:** Buzzer polarity is reversed, or the pin number is wrong.
* **Solution:** Check that the buzzer's VCC goes to pin 6 and GND to GND. Active buzzers have polarity — they won't work backwards.

5. Summary
-------------

You can now control hardware with hand gestures! In this lesson, you learned:

* How gesture classification differs from object detection (one label per frame vs. bounding boxes)
* How change detection prevents repeated triggering
* How to map AI outputs to hardware actions with a clear ``if/else if`` chain
* How to design gesture-based interaction patterns

In the next lesson, you'll build a security system — the camera watches for movement and triggers an alarm when a person enters the frame.
