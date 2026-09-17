.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

Getting Started with AI Camera
==================================

Welcome to Edge AI! Before you can teach the UNO Q to see and recognize objects, you need to make sure the camera itself is working. This quick lesson — about 10 minutes — walks you through installing the camera, verifying the connection, and seeing your first live preview.

.. note::

   This lesson has no AI. No model, no detection, no code to write. Just the camera. If you've already set up the camera in the IoT module, you can skip to the **Take a Photo** step to confirm everything still works.

1. Setup
----------

**What You Need**

.. list-table::
   :widths: 25 25
   :header-rows: 0

   * - 1 * Pan Tilt Kit
     - 1 * USB Cable
   * - |list_pan_tilt|
     - |list_usb_cable|

**Step 1: Attach the Camera**

#. Locate the **CSI connector** on the Multimedia Carrier. It's a small rectangular slot, usually labeled "CAMERA".

#. Open the connector latch by gently lifting the black or white tab. Do not force it — it swings up on a hinge.

#. Insert the **FFC (Flat Flexible Cable)** ribbon with the **blue side facing up** (or metal contacts facing down, depending on your carrier model — check the orientation before closing).

#. Close the latch to secure the cable. The cable should not pull out when gently tugged.

#. Attach the Multimedia Carrier to the UNO Q via the bottom high-speed connector.

.. image:: img/1_camera_setup.png
   :width: 600
   :align: center

.. warning::

   The FFC cable is delicate. Do not crease or fold it sharply. If the camera doesn't work, re-seating the cable is the first thing to try — it's the most common failure point.

**Step 2: Enable the Camera in App Lab**

#. Open **Arduino App Lab**.

#. Go to **Settings → Carriers**.

#. Check **Enable external carriers connected to your Arduino UNO Q**.

#. Select Camera → **type1-2lanes**.

#. Reboot the board.

2. Camera Preview
-------------------

Now let's confirm the camera works. Import and run the Camera Snapshot project from the Multimedia module:

.. code-block:: text

   unoq-ai-kit/media/08 Camera Snapshot.zip

#. Open **Arduino App Lab**, go to **Apps**. Import the **Camera Snapshot** project from your computer.

#. Click **Run** (▶).

#. Open the **Web UI** tab. You should see a live video feed from the camera.

#. Wave your hand in front of the camera — the image should update in real time.

If you see the feed: **your AI camera is ready!**

If the screen is black: see the :ref:`Camera Troubleshooting <camera_troubleshooting>` page.

3. Take a Photo
-----------------

As a final check, use the terminal to capture a still image:

.. code-block:: bash

   cam -c 1 -C1 -s "width=1280,height=720,pixelformat=BGR888" -F"/home/arduino/frame_#.ppm"

This saves a photo to ``/home/arduino/``. If the image looks correct, the camera hardware is confirmed working at every level — from the sensor to the filesystem.

4. What's Next
----------------

🎉 **If you can see the live preview, your AI Camera is ready!**

In the next lesson, you'll run an AI model that can recognize cups, people, and phones — all directly on the UNO Q. No more manual photo capture. The camera will *think*.
