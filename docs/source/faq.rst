.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

FAQ
===

Packages and downloads
----------------------

How do I import a lesson package?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every lesson page and every project README links to its own package on the
`releases page <https://github.com/sunfounder/unoq-ai-kit/releases/latest>`_.
Download that file, then:

#. In App Lab, go to **Apps** → **Create new app** → **Import App** →
   **Import from Computer**.

   .. image:: /img/app_import_app.png
      :width: 600

#. Select the ``.zip`` file you downloaded and click **Open**.

   .. image:: /img/app_import_pc.png
      :width: 600

#. The app appears in **Apps** — click it to open it, then click the **Run**
   button (▶) to upload it to the UNO Q.

   .. image:: /img/app_run.png
      :width: 500

GitHub rewrites spaces in the file names it publishes, so the package for
``01 Hello LED`` downloads as ``01.Hello.LED.zip``. The contents are
identical and the app inside keeps its name.

The speech lessons bundle the bricks they need, which is why those packages
are about 100 MB; the rest are a few hundred kilobytes.

Why are some lesson packages about 100 MB?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The speech lessons carry the bricks they need inside the package, including the
Whisper model used for local speech recognition, which is what makes those
packages large. Every other package is a few hundred kilobytes.

The downloaded package name is not what the lesson says
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

GitHub rewrites spaces in the file names it publishes, so ``01 Hello LED`` is
published as ``01.Hello.LED.zip``. The contents are identical and the app
inside keeps its name. See :doc:`/get_start/download_code`.

Why does a lesson take so long the first time?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Several lessons download something the first time they run — the text to
speech runtime, the speech recognition model, or an AI model. That download
happens once. If an app sits at "starting" for a few minutes, let it finish.

Which lessons need an Internet connection?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lessons that speak, that ask a cloud AI model a question, or that use Arduino
Cloud or Blynk need the Internet. The rest — vision, sensors, motors, the LED
matrix, local speech recognition — run entirely on the board.


App Lab basics
--------------

New to App Lab?
~~~~~~~~~~~~~~~

Arduino documents App Lab itself — apps, bricks, the editor, publishing — at
`Arduino App Lab documentation <https://docs.arduino.cc/software/app-lab/>`_.
For the board's hardware, see
`Arduino UNO Q <https://www.arduino.cc/en/uno-q/>`_.

Where do I see what an app is printing?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open the app in App Lab and watch its console while it runs. The lessons refer
to those lines — ``[READY]``, ``[HEARD]``, and so on — so you can follow what
the code is doing. Arduino documents the app window in `Run and Monitor Apps
<https://docs.arduino.cc/software/app-lab/apps/run/>`_.

Can more than one app run at a time?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No. The UNO Q runs one app at a time, so starting a lesson stops whatever was
running. If **Run** answers that another app is running, stop that app first.

.. _run_button_does_nothing:

Run button does nothing
~~~~~~~~~~~~~~~~~~~~~~~

If the **Run** button (▶) doesn't respond or your board doesn't appear in App Lab:

* Check the USB-C cable is firmly connected at both ends.
* Try unplugging and re-plugging the cable.
* Make sure your UNO Q is detected in App Lab.


.. _install_update_lib_c:

Install or Update Sketch Libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you import a ``.zip`` file, App Lab may list the libraries the app needs under **Sketch Libraries**. They are installed automatically, so there is nothing to do.


Or, when you run the app, you may see an error like ``fatal error: xxxx.h: No such file or directory``.

You can install or update the missing library. Follow the two steps below.

#. Click **Add Sketch Library**.

   .. image:: img/faq_add_lib_c.png

#. Search for the library named in the error message — for example, ``RobotShield``.

   .. image:: img/faq_install_lib_c.png



Note: To ensure the UNO Q board is properly detected by the Arduino App Lab, your user account must have specific write permissions for the USB device. Without these permissions, the board may not appear in the application or allow connections. Please refer to the Linux Host Setup section in the UNO Q User Manual to install the necessary udev rules.

https://docs.arduino.cc/tutorials/uno-q/user-manual/#linux-host-setup-required-for-linux-users


App Lab says a library is missing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a project needs a library that is not installed yet, App Lab lists it
under **Sketch Libraries**. Follow :ref:`install_update_lib_c` to install or
update it, then run the app again.


The board itself
----------------

The board cannot be reached any more
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The board keeps its name when its address changes, so ``jojo.local`` usually
still works when an old IP address does not. App Lab finds the board by itself;
this only matters if you connect from a terminal.

The board is running out of space
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Apps bring their own runtimes with them, so a board that has run many lessons
fills up. Deleting the apps you no longer use frees the space again.

Flashing a New Image to the UNO Q
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Short two pins together, then plug in the UNO Q.

.. An image showing which two pins to short is still needed.

https://docs.arduino.cc/tutorials/uno-q/update-image/

Download the Arduino Flasher CLI for your OS (macOS / Linux / Windows): https://www.arduino.cc/en/software/#flasher-tool


Unzip the downloaded file, (you will receive an executable binary named arduino-flasher-cli)


Navigate to the unzipped folder (e.g. arduino-flasher-cli-x.x.x-windows-amd64), and run the following command:

On Windows, run the following command:


./arduino-flasher-cli.exe flash latest


Camera
------

The camera lessons do not work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The camera needs external carriers enabled on the UNO Q. That is a one-time
setup, described in :ref:`enable_external_carriers`. Cameras are also not
hot-swappable: disconnect the USB-C cable before you plug one in.

.. _enable_external_carriers:

Enable External Carriers (one-time setup)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before you can use the camera, you must enable external carriers on your
UNO Q. This is a **one-time setup** — once enabled, it stays enabled for
every project.

#. On the App Lab home page, click the **Settings** button.

   .. image:: /img/app_settings.png
      :width: 500
      :align: center

#. Turn on **Enable external carriers connected to your Arduino UNO Q**.
   A prompt appears, telling you to plug in the carriers while the board
   is powered off.

   .. image:: /img/app_enable_carrier.png
      :width: 500
      :align: center

#. Check which connector your camera is plugged into — for example, if it
   is on **Camera0**, select the matching type (e.g. **type1-2lanes**) for
   Camera0. Then click **Apply and Reboot**.

   .. image:: /img/app_camera0.png
      :width: 500
      :align: center

.. _single_camera_only:

.. warning::

   If you are using a **single camera**, enable only the connector it is
   plugged into — **Camera0** or **Camera1** — and leave the other one set
   to **none**. Enabling **both** Camera0 and Camera1 at the same time makes
   the App fail to detect the camera.


.. _check_camera_detected:

How do I check that the camera is detected?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The camera works as soon as external carriers are enabled
(:ref:`enable_external_carriers`). If a camera lesson still cannot find the
sensor, connect to the board from a terminal and work through these checks —
they separate a wrong carrier setting from a loose cable.

**List the cameras the system can see**

.. code-block:: bash

   cam -l

This is the most reliable check. A working camera appears under
**Available cameras**, followed by its sensor path, for example:

.. code-block:: text

   Available cameras:
   1: 'imx219' (/base/soc@0/cci@5c1b000/i2c-bus@0/sensor@10)

The path also tells you the I2C bus and address — ``i2c-bus@0`` and
``sensor@10`` mean bus **0**, address **0x10**. If nothing is listed, the
carrier is not enabled or the FFC cable is not seated; go back to
:ref:`enable_external_carriers`.

**Capture a test frame**

.. code-block:: bash

   cam -c 1 -C1 -s "width=1280,height=720,pixelformat=BGR888" -F"/home/arduino/frame_#.ppm"

A ``Capture 1 frames`` line means the whole stack works. The frames are
written to the ``arduino`` home folder.

**Confirm the sensor answers on the I2C bus**

Use the bus number from the ``cam -l`` output above — it is usually **0**,
but it can differ, so do not assume one:

.. code-block:: bash

   sudo i2cdetect -l          # list the buses; the camera sits on a Qualcomm-CCI bus
   sudo i2cdetect -y 0        # replace 0 with the bus number from cam -l

The camera shows as ``UU`` at address ``0x10``. You can also read its name
directly:

.. code-block:: bash

   sudo cat /sys/class/i2c-dev/i2c-0/device/0-0010/name

A working camera prints ``imx219``. If the address is missing, re-seat the
FFC cable (the blue side faces up) and check the carrier setting again.

.. note::

   ``dmesg | grep imx219`` and ``ls /dev/video*`` are **not** reliable on this
   board — the kernel log is often empty even when the camera works, and the
   ``/dev/video*`` devices exist whether or not a camera is attached. Trust
   ``cam -l`` and the capture test instead.

**List the carriers and their camera configuration**

.. code-block:: bash

   sudo arduino-linux-config carrier list

**Set the camera channel from the command line**

This is the same setting as **Settings → carriers** in App Lab. Match the
channel to the connector the camera is plugged into.

.. code-block:: bash

   # Camera 1 connector, 2-lane
   sudo arduino-linux-config carrier enable media-carrier camera0=none camera1=type1-2lanes

   # Camera 1 connector, 4-lane
   sudo arduino-linux-config carrier enable media-carrier camera0=none camera1=type1-4lanes

   sudo reboot

For a camera on the **Camera 0** connector, move the setting to ``camera0`` —
for example ``camera0=type1-2lanes camera1=none``.

**Update the system**

If the camera is detected but an app cannot open it, make sure the board is
up to date:

.. code-block:: bash

   arduino-app-cli system update


.. _camera_troubleshooting:
.. _camera_detected_app_fails:

The camera is detected, but a camera app still fails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**"No camera found" in App Lab**

* **Cause:** The FFC cable is loose or inserted backwards, or both camera channels are enabled for a single camera.
* **Solution:** Re-seat both ends of the FFC cable — the blue side faces up, and the connectors click when closed. Then check that only the connector you actually use is enabled: :ref:`single camera only <single_camera_only>`.

**Black screen in the Web UI, but cam -l lists the camera**

* **Cause:** The app is not starting its camera service.
* **Solution:** Make sure the camera brick the lesson uses is declared under ``bricks:`` in ``app.yaml``, then stop and run the app again.

**The camera works in the terminal but not in Python**

* **Cause:** The CSI image arrives upside-down on the AVIO Carrier.
* **Solution:** Add the vertical flip when the camera is opened: ``Camera(adjustments=lambda frame: frame[::-1,:])``.

**"Permission denied" when running cam or i2cdetect**

* **Cause:** These commands need root privileges.
* **Solution:** Prefix them with ``sudo`` (for example ``sudo cam -l``, ``sudo i2cdetect -y 0``).


Sound and speech
----------------

The voice lessons do not hear me
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two things are worth checking, in this order. First, whether the microphone
picks up anything at all — speak from 30–50 cm in a quiet room. Second, the
wake-word model shipped with the board was trained on one speaker's voice, so
it recognises some voices better than others; the lesson console prints what
the model made of every window of audio, which shows whether the microphone or
the model is the problem.


AI models and Edge Impulse
--------------------------

Where can I learn more about Edge Impulse?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Edge Impulse documents the same workflow in more depth. The course keeps the
Arduino-specific steps — setting the target, deploying, and downloading the model
in App Lab — that these pages leave out:

* `Image classification <https://docs.edgeimpulse.com/tutorials/end-to-end/image-classification>`_ — the end-to-end training tutorial this course follows
* `Run Arduino App Lab <https://docs.edgeimpulse.com/hardware/deployments/run-arduino-app-lab>`_ — deploying a model for the UNO Q
* `Custom AI models for Arduino App Lab <https://docs.arduino.cc/software/app-lab/integrations/ai-models/>`_ — Arduino's own walkthrough

An app will not start after adding a second video AI brick
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every video AI brick opens the live preview on port **4912**, so an app can hold
only one of them. Adding a second one — a ``video_image_classification`` brick next to an
existing ``video_object_detection`` brick, for example — stops the app with a message
such as ``Bind for :::4912 failed: port is already allocated``.

Open the app's ``app.yaml`` in the App Lab editor and keep just one video brick,
deleting the others, then run the app again. Classification and detection both
fit a camera app; keep the one that matches the model you trained.

A model shows one result when there are two identical objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

That is what an **image classification** model does: it answers for the whole
picture — "this is a card reader" — instead of listing every object it can
find. Two identical objects therefore produce one result with one confidence,
and the class totals count how often each class won, not how many objects were
in the frame.

An **object detection** model returns one result per object, each with a box or
a centre point, so two objects give two results. Training one takes longer,
because every training image has to be annotated with a box around each
object. In App Lab, classification models run on the ``image_classification``
and ``video_image_classification`` bricks, and detection models on ``object_detection``
and ``video_object_detection``.


Text to speech and speech to text
-------------------------------------

The board stops talking, and the console shows a 403 from speech.platform.bing.com
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Cause:** the EdgeTTS engine talks to a free service that Microsoft runs for the
Edge browser's Read Aloud feature. Microsoft changes the handshake token without
notice, and an older copy of the engine then gets a 403.

**Solution:** download the latest package for that lesson again — the current
packages pin the engine to a version that speaks the new handshake, and they fall
back to the offline **espeak** engine if the online service fails again, so the
board keeps talking even when the service changes. If you maintain your own copy,
re-pin it with ``"edge-tts>=7.3.1"`` and rebuild the brick image.

API keys and cloud services
---------------------------

Where do I enter an API key, and how do I change it?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lessons that use a cloud AI model ask for the key the first time you click
**Run**. App Lab stores it, so you only enter it again if it changes. Cloud
platforms such as Arduino Cloud and Blynk also give you a **Device ID** and a
**Secret Key** — save them when they are generated, because the lesson needs
them later.

.. _llm_other_models:

Can I use a model from another provider?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


The ``cloud_llm`` brick is not tied to OpenAI. It speaks to **OpenAI**, **Anthropic
(Claude)** and **Google (Gemini)** through the same API, and the model name each lesson
passes to ``CloudLLM(...)`` is what picks the provider:

.. code-block:: python

   llm = CloudLLM(
       model="openai:gpt-4o-mini",   # what the lessons use
       system_prompt=...,
   )

Everything before the colon is the **provider** - ``openai``, ``anthropic`` or ``google`` -
and everything after it is any model id that provider publishes. A name with no provider
prefix is treated as OpenAI, so switching is a one-line change:

.. code-block:: python

   llm = CloudLLM(model="anthropic:<model-id>", system_prompt=...)

The brick also exposes an enum that always points at the provider's current model, so you
never have to type a model id:

.. code-block:: python

   from arduino.app_bricks.cloud_llm import CloudLLM, CloudModel

   llm = CloudLLM(model=CloudModel.ANTHROPIC_CLAUDE, system_prompt=...)

Two things stay the same whatever you choose:

* **The API key.** The brick reads it from its ``API_KEY`` variable - the field App Lab asks
  you to fill in the first time the app runs. Paste the key **for the provider you picked**;
  App Lab keeps it on the board.
* **The rest of the project.** System prompts, temperature and the streaming calls are
  provider-independent, so nothing else in the code changes.

