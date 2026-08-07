.. _camera_troubleshooting:

Camera Troubleshooting
=========================

If the camera preview shows a black screen or you see "No camera detected" errors, use the commands below to diagnose the problem. Run them in App Lab's terminal or via SSH.

.. tip::

   **The golden rule of hardware debugging:** check at the lowest level first. If the operating system can't see the camera, no amount of code will help. Work your way up: kernel → device file → user-space tool → application code.

---

Check 1: Is the camera sensor detected?
------------------------------------------

.. code-block:: bash

   dmesg | grep imx219

Expected output (example):

.. code-block:: text

   [    2.123456] imx219 3-0010: imx219_probe(): camera found

If you see nothing, the sensor is not being detected by the Linux kernel. Check the FFC cable connection and ensure the camera is enabled in Settings → Carriers.

---

Check 2: Are I2C devices visible?
------------------------------------

.. code-block:: bash

   sudo i2cdetect -l

Look for I2C buses that mention "Qualcomm-CCI" or "Geni-I2C". The camera sensor appears on one of these buses.

.. code-block:: bash

   sudo i2cdetect -y 3

Look for ``UU`` at address 0x10 — this indicates the imx219 sensor is registered.

You can also confirm the device name:

.. code-block:: bash

   sudo cat /sys/class/i2c-dev/i2c-3/device/3-0010/name

Expected: ``imx219``

---

Check 3: Does a video device exist?
--------------------------------------

.. code-block:: bash

   ls /dev/video*

If the camera is working, you should see at least one ``/dev/video0`` (or similar). If this directory is empty, the camera driver hasn't created a video device — go back to Check 1.

---

Check 4: Can user-space tools see the camera?
------------------------------------------------

.. code-block:: bash

   cam -l

This lists all cameras available to the ``cam`` command-line tool. Look for entries under "Available" — these are cameras ready for use.

---

Check 5: Can you capture a test image?
-----------------------------------------

.. code-block:: bash

   cam -c 1 -C1 -s "width=1280,height=720,pixelformat=BGR888" -F"/home/arduino/frame_#.ppm"

If this produces a valid image file, the camera hardware and software stack are working correctly.

---

Check 6: Is the camera configured correctly in App Lab?
----------------------------------------------------------

#. Go to **Settings → Carriers** in App Lab.
#. Make sure **Enable external carriers** is checked.
#. Under Camera, select **type1-2lanes** (for a single camera on a 2-lane CSI bus).
#. **Reboot** the board after changing this setting.

---

Common Issues
---------------

**Black screen in Web UI, but ``cam -l`` shows the camera**

* **Cause:** The ``VideoObjectDetection`` brick may not be starting the video stream service.
* **Solution:** Make sure ``video_object_detection`` is listed under ``bricks:`` in ``app.yaml``. Without this brick, the camera feed won't reach the browser on port 4912.

**"No camera found" in App Lab**

* **Cause:** The FFC cable is loose or inserted backwards.
* **Solution:** Re-seat both ends of the FFC cable. The blue side faces up on most carriers. The connectors should click when closed.

**Camera works in terminal but not in Python code**

* **Cause:** The CSI camera adjustment is missing.
* **Solution:** Make sure the code uses ``Camera(adjustments=lambda frame: frame[::-1,:])`` — the camera is mounted upside-down on the Multimedia Carrier by default, and the frame needs to be flipped vertically.

**"Permission denied" when running cam or i2cdetect**

* **Cause:** These commands require root privileges.
* **Solution:** Prefix with ``sudo`` (e.g., ``sudo cam -l``, ``sudo i2cdetect -y 3``).
