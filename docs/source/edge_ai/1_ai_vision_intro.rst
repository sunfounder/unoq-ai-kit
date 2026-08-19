.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

1. AI Vision Recognition
============================

In the IoT module, you saw the camera feed on a webpage. Now you'll give the camera a brain — the UNO Q runs a pre-trained AI model that **recognizes objects** in real time. Point it at a cup, a person, or a phone, and the model identifies what it sees, right on the device.

In this lesson, you will learn to:

* Run a pre-trained object detection model on the UNO Q
* View AI recognition results — object name and confidence score — in the Web UI
* Understand the pipeline: camera → AI model → socket.io → browser

1. Setup
----------

**What You Need**

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 0

   * - 1 * :ref:`Arduino Uno Q <cpn_uno_q>`
     - 1 * Multimedia Carrier
     - 1 * CSI Camera
     - 1 * USB Cable
   * - |list_uno_q|
     - |list_uno_q|
     - |list_uno_q|
     - |list_usb_cable|

.. note::

   The Multimedia Carrier and camera should already be attached. If not, refer to the setup guide before proceeding. The camera must be enabled in App Lab Settings → Carriers → Camera → **type1-2lanes** → Reboot.

**Hardware Check**

#. Make sure the camera's FFC ribbon cable is securely connected to a CSI connector on the Multimedia Carrier. The blue side of the cable faces up.

#. Attach the Multimedia Carrier to the UNO Q via the bottom connector.

#. Connect the UNO Q to your computer with the USB-C cable.

#. In App Lab, go to **Settings → Carriers** → Enable external carriers → Camera → **type1-2lanes** → Reboot the board.

.. image:: img/1_camera_setup.png
   :width: 600
   :align: center

2. Code
----------

**Import the Code**

#. Open **Arduino App Lab**, go to **Apps**. Click the dropdown arrow next to **Create new app +** and select **Import App**.

   .. image:: /img/app_import_app.png
      :width: 600
      :align: center

#. Select **Import from Computer**.

   .. image:: /img/app_import_pc.png
      :width: 600
      :align: center

#. Navigate to the ``unoq-ai-kit/edge_ai/`` folder and select ``01 AI Vision Recognition.zip``.

#. The app appears in **Apps** — click it to open.

**Run the Code**

#. Click the **Run** button (▶). The app initializes the camera and loads the AI model.

#. Once running, open the **Web UI** tab. You'll see the live camera feed on the left and a detection results panel on the right.

#. Hold up a cup, your phone, or have a friend stand in front of the camera. The AI identifies each object and displays its name and confidence score.

**How it Works**

.. code-block:: text

   Camera (CSI)
       │
       ▼
   VideoObjectDetection brick (general model)
       │
       ├── Video stream → port 4912/embed → <iframe> in Web UI
       │
       └── Detections → socket.io → detection panel in Web UI

The project runs almost entirely on the Linux MPU side. The ``VideoObjectDetection`` brick handles three things at once: opening the camera, running the AI model on every frame, and streaming both the video and the detection results to the browser.

* **Camera capture** — Each frame from the CSI camera is flipped vertically (the camera is mounted upside-down on the carrier), then fed into the model.
* **AI model** — A general object detection model that recognizes ~80 common object categories. It runs locally on the UNO Q — no cloud, no internet required.
* **Video stream** — The processed frames (with bounding boxes) are served on port 4912. The Web UI embeds this stream via an ``<iframe>``.
* **Detection results** — Each detected object is sent to the browser via socket.io with its name and confidence score (0–100%).

3. Experiment
----------------

**Test Different Objects**

Try showing these objects to the camera and observe the results:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Object
     - Expected Result
   * - Coffee cup or mug
     - "cup" with high confidence (>80%)
   * - Smartphone
     - "cell phone" with high confidence
   * - A person's face
     - "person" with high confidence
   * - A bottle
     - "bottle" with high confidence

**Challenge: Lighting Conditions**

Test the model under different lighting — bright room, dim room, backlight from a window. At what point does it start to fail? Edge AI models are sensitive to lighting because they were trained on well-lit images.

**Challenge: Distance Test**

Find the maximum distance at which the model can still reliably detect your face. Move 1 meter away, then 2, then 3. How does distance affect confidence?

4. Troubleshooting
--------------------

**Web UI shows a black screen (no camera feed)**

* **Cause:** The camera is not enabled, or the FFC cable is loose.
* **Solution:** Go to Settings → Carriers → enable Camera → type1-2lanes → Reboot. Check the camera cable: blue side faces up, both ends must click securely.

**Model loads but never detects anything**

* **Cause:** The camera is facing the wrong direction, or lighting is too poor.
* **Solution:** Point the camera at a well-lit object within 1–2 meters. Make sure nothing is blocking the lens. The model works best with objects centered in the frame.

**"Connection lost" error in Web UI**

* **Cause:** The app isn't running, or the board disconnected.
* **Solution:** Click **Run** in App Lab. Check the USB-C cable is firmly connected at both ends. Try unplugging and re-plugging.

**Run button does nothing**

* **Cause:** The board is not connected, or App Lab can't find it.
* **Solution:** Check the USB-C cable. Try unplugging and re-plugging it. In App Lab, make sure your UNO Q is detected.

5. Summary
-------------

You just ran AI vision on a microcontroller! In this lesson, you learned:

* How the ``VideoObjectDetection`` brick handles camera, AI model, and streaming all in one
* How object detection works: capture frame → run model → display results
* How the video stream and detection data travel to the browser through different channels (iframe + socket.io)

In the next lesson, you'll connect AI to physical hardware — when a face is detected, a buzzer sounds an alarm.
