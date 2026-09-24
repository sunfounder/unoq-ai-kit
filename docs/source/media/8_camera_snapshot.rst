.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

08 Camera Snapshot
====================

The AVIO Carrier doesn't just speak and listen — it has eyes too. In this lesson you'll use the built-in camera: press the button, and the board captures a photo and saves it to the ``photos`` folder with automatic numbering. One press, one picture.

In this lesson, you will learn to:

* Start the camera with the App Lab ``Camera`` peripheral
* Capture a single frame with ``camera.capture()``
* Flip an image with OpenCV to correct its orientation
* Generate never-overwriting filenames like ``photo_001.jpg``

1. Setup
----------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * :ref:`cpn_button`
     - 1 * :ref:`cpn_breadboard`
     - Several :ref:`cpn_wires`
   * - |list_pan_tilt|
     - |list_button|
     - |list_breadboard|
     - |list_wire|
   * - 1 * USB Cable
     - -
     - -
     - -
   * - |list_usb_cable|
     - -
     - -
     - -

**Software Requirements**

This project uses no Bricks — the camera is an App Lab **peripheral** that comes with App Lab itself. The sketch only uses the built-in Bridge framework, so there are no libraries to install.

Before using the camera, make sure external carriers are enabled on your UNO Q — this is a one-time setup: :ref:`enable_external_carriers`.

**Wiring Diagram**

Connect the push button between D4 and GND — no external resistor is needed, the sketch uses the internal pull-up resistor. The camera is built into the AVIO Carrier.

.. image:: /img/wiring/wiring_button.png
   :width: 500
   :align: center

2. Run the App
----------------

#. Download :download:`08 Camera Snapshot.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/08.Camera.Snapshot.zip>`.
#. In App Lab, go to **Apps** → **Create new app** → **Import App** → **Import from Computer**, and open the package you downloaded.
#. Click **Run** (▶). The Output window shows:

   *"Camera ready. Press the button to take a photo."*

#. Point the camera at something interesting and press the button. The Output window shows **Photo saved: photos/photo_001.jpg** — press again for ``photo_002.jpg``, then ``photo_003.jpg``, and so on.

**How it Works**

.. mermaid::

   sequenceDiagram
       participant B as Button (D4)
       participant S as Sketch (sketch.ino)
       participant P as Python (main.py)

       loop every 0.05 s
           P->>S: Bridge.call("button_read")
           S-->>P: 0 or 1
       end
       Note over P: press edge (0 → 1)
       P->>P: camera.capture() → one frame
       P->>P: cv2.flip(frame, 0)
       P->>P: next_photo_path() → "photos/photo_001.jpg"
       P->>P: cv2.imwrite(...) → save

* The camera is an App Lab **peripheral**, not a Brick — you import it from ``arduino.app_peripherals.camera`` and start it with ``camera.start()``. It keeps running in the background, and ``camera.capture()`` grabs the latest frame.
* The camera sits upside down on the pan-tilt mount, so every frame is flipped vertically with ``cv2.flip(frame, 0)`` before saving.
* ``next_photo_path()`` scans for the first unused number — ``photo_001.jpg``, then ``photo_002.jpg``, and so on. Because it checks what already exists, restarting the app never overwrites previous photos.
* The same edge detection from the earlier button lessons is used: a photo is captured only when the button **changes** from released to pressed, so holding the button down still takes exactly one photo.

3. Experiment
----------------

**Take a Photo Series**

Press the button five times and check the ``photos`` folder after each press:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - You do
     - Result
   * - Press once
     - ``photos/photo_001.jpg`` appears
   * - Press again
     - ``photos/photo_002.jpg`` appears — the first photo is untouched
   * - Press and **hold**
     - One new photo — no extra photos while held
   * - Stop and run again, then press
     - ``photo_003.jpg`` — old photos are still there

**Change Where Photos Are Saved**

In ``main.py``, change the target folder:

.. code-block:: python

   PHOTO_DIR = Path("/app/photos")

   # becomes

   PHOTO_DIR = Path("/app/my_snapshots")

New photos now appear in ``my_snapshots`` instead — the folder is created automatically.

**Challenge: Keep Only the Latest Five Photos**

Modify ``next_photo_path()`` so the app never keeps more than five photos: before saving a new one, delete the oldest files when more than five exist. You'll need the ``Path`` methods ``glob()`` (to list files), ``stat().st_mtime`` (to find the oldest), and ``unlink()`` (to delete) — or sort by name instead of time.

4. Troubleshooting
--------------------

**"Initializing camera..." never finishes**

* **Cause:** The AVIO Carrier isn't properly attached, or the camera is busy.
* **Solution:** Check that the Carrier is firmly connected to the UNO Q, then stop and run the app again.

**The photo is upside down**

* **Cause:** The ``cv2.flip(frame, 0)`` line is missing or commented out.
* **Solution:** Make sure the flip runs before ``cv2.imwrite()`` — the camera sits upside down on the pan-tilt mount.

**"Failed to save photo." appears after every press**

* **Cause:** The target folder doesn't exist and couldn't be created.
* **Solution:** The code creates ``PHOTO_DIR`` at startup with ``mkdir(parents=True, exist_ok=True)`` — make sure that line runs before the loop.

**The photo is dark or blurry**

* **Cause:** Not enough light, or the board moved while capturing.
* **Solution:** Point the camera at a well-lit subject and hold the board still for a moment after pressing the button.

5. Summary
-------------

The UNO Q can now see and save what it sees! In this lesson, you learned:

* How to start the App Lab ``Camera`` peripheral
* How ``camera.capture()`` grabs a single frame
* Why ``cv2.flip()`` corrects the camera's upside-down orientation
* How ``next_photo_path()`` numbers photos without ever overwriting

In the next lesson, everything comes together — voice commands will control both the pan-tilt and the camera.
