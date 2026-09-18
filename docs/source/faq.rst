.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

FAQ
===============


How do I import a lesson package?
----------------------------------

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

Why does a lesson take so long the first time?
----------------------------------------------

Several lessons download something the first time they run — the text to
speech runtime, the speech recognition model, or an AI model. That download
happens once. If an app sits at "starting" for a few minutes, let it finish.

Which lessons need an Internet connection?
-------------------------------------------

Lessons that speak, that ask a cloud AI model a question, or that use Arduino
Cloud or Blynk need the Internet. The rest — vision, sensors, motors, the LED
matrix, local speech recognition — run entirely on the board.

Why are some lesson packages about 100 MB?
-------------------------------------------

The speech lessons carry the bricks they need inside the package, including the
Whisper model used for local speech recognition, which is what makes those
packages large. Every other package is a few hundred kilobytes.

App Lab says a library is missing
----------------------------------

When a project needs a library that is not installed yet, App Lab lists it
under **Sketch Libraries**. Follow :ref:`install_update_lib_c` to install or
update it, then run the app again.

The camera lessons do not work
-------------------------------

The camera needs external carriers enabled on the UNO Q. That is a one-time
setup, described in :ref:`enable_external_carriers`. Cameras are also not
hot-swappable: disconnect the battery and the USB cable before you plug one in.

The voice lessons do not hear me
---------------------------------

Two things are worth checking, in this order. First, whether the microphone
picks up anything at all — speak from 30–50 cm in a quiet room. Second, the
wake-word model shipped with the board was trained on one speaker's voice, so
it recognises some voices better than others; the lesson console prints what
the model made of every window of audio, which shows whether the microphone or
the model is the problem.

Where do I enter an API key, and how do I change it?
-----------------------------------------------------

Lessons that use a cloud AI model ask for the key the first time you click
**Run**. App Lab stores it, so you only enter it again if it changes. Cloud
platforms such as Arduino Cloud and Blynk also give you a **Device ID** and a
**Secret Key** — save them when they are generated, because the lesson needs
them later.

Can more than one app run at a time?
-------------------------------------

No. The UNO Q runs one app at a time, so starting a lesson stops whatever was
running. If **Run** answers that another app is running, stop that app first.

Where do I see what an app is printing?
----------------------------------------

Open the app in App Lab and watch its console while it runs. The lessons refer
to those lines — ``[READY]``, ``[HEARD]``, and so on — so you can follow what
the code is doing. Arduino documents the app window in `Run and Monitor Apps
<https://docs.arduino.cc/software/app-lab/apps/run/>`_.

The downloaded package name is not what the lesson says
--------------------------------------------------------

GitHub rewrites spaces in the file names it publishes, so ``01 Hello LED`` is
published as ``01.Hello.LED.zip``. The contents are identical and the app
inside keeps its name. See :doc:`/get_start/download_code`.

The board cannot be reached any more
-------------------------------------

The board keeps its name when its address changes, so ``jojo.local`` usually
still works when an old IP address does not. App Lab finds the board by itself;
this only matters if you connect from a terminal.

The board is running out of space
----------------------------------

Apps bring their own runtimes with them, so a board that has run many lessons
fills up. Deleting the apps you no longer use frees the space again.

New to App Lab?
----------------

Arduino documents App Lab itself — apps, bricks, the editor, publishing — at
`Arduino App Lab documentation <https://docs.arduino.cc/software/app-lab/>`_.
For the board's hardware, see
`Arduino UNO Q <https://www.arduino.cc/en/uno-q/>`_.

.. _run_button_does_nothing:

Run button does nothing
-----------------------------------------

If the **Run** button (▶) doesn't respond or your board doesn't appear in App Lab:

* Check the USB-C cable is firmly connected at both ends.
* Try unplugging and re-plugging the cable.
* Make sure your UNO Q is detected in App Lab.


.. _install_update_lib_c:

安装或更新Sketch库
-----------------------------------------

When you import a ``.zip`` file, App Lab may list the libraries the app needs under **Sketch Libraries**. They are installed automatically, so there is nothing to do.


或者当你运行时，显示报错 ``fatal error: xxxx.h: No such file or directory``

你可以去安装或更新对应的库。现在参考下面两个步骤。

#. 点击**Add Sketch Library**

   .. image:: img/faq_add_lib_c.png

#. 搜索文档上提示的库的比如，比如RobotShield

   .. image:: img/faq_install_lib_c.png



Note: To ensure the UNO Q board is properly detected by the Arduino App Lab, your user account must have specific write permissions for the USB device. Without these permissions, the board may not appear in the application or allow connections. Please refer to the Linux Host Setup section in the UNO Q User Manual to install the necessary udev rules.

https://docs.arduino.cc/tutorials/uno-q/user-manual/#linux-host-setup-required-for-linux-users


.. _enable_external_carriers:

Enable External Carriers (one-time setup)
-------------------------------------------

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



Flashing a New Image to the UNO Q
-------------------------------------------


需要短接2个引脚，然后插入UNO Q

<此处需要配张图>

https://docs.arduino.cc/tutorials/uno-q/update-image/

Download the Arduino Flasher CLI for your OS (MacOS / Linux / Windows)：https://www.arduino.cc/en/software/#flasher-tool


Unzip the downloaded file, (you will receive an executable binary named arduino-flasher-cli)


Navigate to the unzipped folder (e.g. arduino-flasher-cli-x.x.x-windows-amd64), and run the following command:

windows运行下面的命令


./arduino-flasher-cli.exe flash latest

