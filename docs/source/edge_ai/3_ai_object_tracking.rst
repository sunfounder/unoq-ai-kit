.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

3. AI Object Tracking Pan-Tilt
==================================

Now that your UNO Q can see, let's give it the ability to **follow** what it sees. You'll build an AI-powered pan-tilt tracker — the camera detects a face, and the servo motors automatically rotate to keep the face centered in the frame. This is the same technology used in video conferencing cameras and robot vision systems.

In this lesson, you will learn to:

* Use face detection to get the position of a face in the camera frame
* Control two servos (pan and tilt) based on AI output
* Implement a simple tracking loop: detect → calculate offset → move → repeat
* Tune tracking speed and smoothness

1. Build the Circuit
----------------------

**Components Needed**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * :ref:`Arduino Uno Q <cpn_uno_q>`
     - 1 * Multimedia Carrier
     - 1 * Camera Module
     - 2 * :ref:`cpn_servo`
   * - |list_uno_q|
     - |list_uno_q|
     - |list_uno_q|
     - |list_servo|
   * - 1 * Pan-Tilt Mount
     - Several :ref:`cpn_wires`
     - 1 * USB Cable
     -
   * - |list_uno_q|
     - |list_wire|
     - |list_usb_cable|
     -

**Assembly**

#. Attach the two servos to the pan-tilt mount as shown in the diagram below. The bottom servo controls **pan** (left/right), the top servo controls **tilt** (up/down).

#. Mount the camera module onto the top plate of the pan-tilt mount.

#. Connect the pan servo to **digital pin 9**, and the tilt servo to **digital pin 10**.

#. Attach the Multimedia Carrier (with the camera's FFC cable connected) to the UNO Q.

.. image:: img/3_pantilt_assembly.png
   :width: 700
   :align: center

**Circuit Diagram**

.. image:: img/3_pantilt_schematic.png
   :width: 500
   :align: center

The servos receive position commands from the UNO Q. The pan servo sweeps left/right (0–180°), the tilt servo tilts up/down (typically 30–150° to avoid pointing at the ceiling or floor).

2. Code
----------

**Import the Code**

#. In App Lab, go to **My Apps** → **Import App** → **Import from Computer**.

#. Navigate to ``unoq-ai-kit/edge_ai/`` and select ``3_ai_object_tracking.zip``.

#. Open the imported app.

**Run the Code**

#. Click the **Run** button (▶). The servos will center themselves, and the camera will initialize.

#. Stand in front of the camera, about 1–2 meters away. Move slowly left and right — the pan-tilt should follow your face.

#. Open the **Web UI** to see the camera feed with the detected face outlined and the tracking crosshair.

.. image:: img/3_tracking_result.gif
   :width: 600
   :align: center

**The Code**

.. code-block:: cpp
   :linenos:

   /*
    * Lesson 3: AI Object Tracking Pan-Tilt
    * Tracks a face and moves servos to keep it centered.
    */

   #include <Arduino_RouterBridge.h>
   #include <Servo.h>
   #include "camera.h"
   #include "edge_impulse.h"

   Servo panServo;   // Left/right
   Servo tiltServo;  // Up/down

   const int panPin = 9;
   const int tiltPin = 10;

   // Center positions
   int panAngle = 90;
   int tiltAngle = 90;

   // Tracking sensitivity
   const float Kp = 0.1;  // Proportional gain

   void setup() {
       Monitor.begin();
       Camera.begin();
       AI.begin("face_detection.eim");

       panServo.attach(panPin);
       tiltServo.attach(tiltPin);

       // Center the servos
       panServo.write(panAngle);
       tiltServo.write(tiltAngle);
   }

   void loop() {
       Camera.capture();
       AIResult result = AI.classify();

       if (result.detected) {
           // Get the center of the detected face (0.0 to 1.0)
           float faceX = result.centerX;  // Horizontal position
           float faceY = result.centerY;  // Vertical position

           // Calculate offset from frame center (0.5, 0.5)
           float errorX = faceX - 0.5;
           float errorY = faceY - 0.5;

           // Adjust servo angles proportionally
           panAngle += errorX * Kp * 180;
           tiltAngle -= errorY * Kp * 180;

           // Constrain to safe range
           panAngle = constrain(panAngle, 0, 180);
           tiltAngle = constrain(tiltAngle, 30, 150);

           // Move servos
           panServo.write(panAngle);
           tiltServo.write(tiltAngle);

           Monitor.print("Tracking: pan=");
           Monitor.print(panAngle);
           Monitor.print(" tilt=");
           Monitor.println(tiltAngle);
       }
   }

**How it Works**

.. code-block:: text

   setup() → runs once:
       Initialize camera + AI model
       Attach servos to pins
       Center servos at 90°

   loop() → runs forever:
       Capture frame → run face detection
       Face found?
           YES → calculate offset from frame center
               Adjust pan/tilt angles proportionally
               Constrain angles to safe range
               Move servos to new position
           NO  → servos hold last position

Here's what's new in this lesson:

* **Face detection model** — Unlike the general object detection model in Lesson 1, this model is specialized for faces. It returns not just a label but also the face's **bounding box coordinates** (centerX, centerY), which we use to calculate tracking error.
* **Proportional control (Kp)** — The servo movement is proportional to the error — small offset = small movement, large offset = larger movement. The gain ``Kp = 0.1`` controls responsiveness. Too high and the tracker oscillates; too low and it lags behind.
* **Error calculation** — ``errorX = faceX - 0.5`` gives the horizontal offset from frame center. Positive means the face is to the right; negative means it's to the left. The servo adjusts accordingly.
* **``constrain()``** — Clamps a value to a specified range. ``constrain(panAngle, 0, 180)`` ensures the servo never receives a command outside its physical limits, which could damage the motor or the mount.

3. Experiment
----------------

**Tune the Tracking Speed**

Adjust ``Kp`` and observe the effect:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Kp
     - Behavior
   * - ``0.05``
     - Slow, smooth tracking — noticeable lag behind the face
   * - ``0.1`` (default)
     - Balanced — responsive without oscillation
   * - ``0.2``
     - Fast, aggressive tracking — may overshoot and oscillate

**Challenge: Dead Zone**

Add a dead zone: don't move the servos if the face is within 10% of frame center. This prevents jitter when the face is already well-centered:

.. code-block:: cpp

   if (abs(errorX) < 0.1 && abs(errorY) < 0.1) {
       return;  // Face is centered, no movement needed
   }

**Challenge: Track Multiple Objects**

Modify the code to find the largest detected object (by bounding box area) and track that, instead of always tracking the first detection. This makes the tracker more robust in crowded scenes.

4. Troubleshooting
--------------------

**Servos don't move at all**

* **Cause:** Servo power is insufficient, or the pins are wrong.
* **Solution:** Make sure the servos are connected to pins 9 (pan) and 10 (tilt). If using external servo power from the Robot Shield, check that the power rail is enabled.

**Tracker oscillates (shakes back and forth)**

* **Cause:** The proportional gain ``Kp`` is too high.
* **Solution:** Reduce ``Kp`` to ``0.05`` or ``0.03``. Add the dead zone from the Experiment section to prevent small-amplitude oscillation.

**Face detection works but tracker points in the wrong direction**

* **Cause:** Servo direction is reversed for your mount orientation.
* **Solution:** Change the sign of the error calculation. For example, change ``panAngle += errorX * Kp * 180`` to ``panAngle -= errorX * Kp * 180`` to reverse the pan direction.

**Tracking lags badly behind the person**

* **Cause:** Inference is too slow, or ``Kp`` is too low.
* **Solution:** Increase ``Kp`` to ``0.15``. Make sure the camera resolution isn't set too high — 320×240 is ideal for real-time tracking on a microcontroller.

5. Summary
-------------

Your UNO Q can now follow you! In this lesson, you learned:

* How to use face detection coordinates to calculate tracking error
* How proportional control (Kp) creates smooth servo motion
* How to constrain servo angles to safe physical limits
* How to tune a control loop for responsive, stable tracking

In the next lesson, you'll replace the face tracker with gesture recognition — using hand signs to control LEDs and buzzers.
