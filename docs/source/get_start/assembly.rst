.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

.. _pan_tilt_kit:

Assembly
========

Put the kit together before starting the lessons. The two servos have to sit at 90° while you fit the horns, so the first three steps run a small App Lab app that holds them there.

**1. Download the centering app**

:download:`Pan-Tilt Servo Centering.zip <https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/Pan-Tilt.Servo.Centering.zip>` holds both servos at 90° while you work. Save it anywhere you can find it again.

**2. Import it into App Lab**

In Arduino App Lab, click **Apps** → **Create New App** → **Import App** → **Import from Computer**, then choose the file you downloaded.

**3. Turn on Run as Startup**

Switch on **Run as Startup**: both servos swing to their center position and stay there while you assemble.

.. image:: /img/app_run_startup.png
    :width: 70%
    :align: center

**4. Assemble the kit**

With both servos centred, fit the horns and put the two parts together — the **board stack** first, then the **pan-tilt mount**.

#. The **Robot Shield** goes on top of the **UNO Q**. Line up its headers with the UNO Q's pins and press it down firmly until every pin is fully seated.
#. The **AVIO Carrier** plugs into the UNO Q's high-speed connectors. Line up its two sockets with the matching connectors and press it down until it is fully seated.
#. Mount the **pan servo** on the base of the mount, then the **tilt servo** and the camera bracket on top of the pan section.
#. Attach the **camera** to the tilt bracket and connect its FPC cable to the AVIO Carrier — see :doc:`/avio_carrier`.
#. Plug the pan servo into **D9** and the tilt servo into **D10** on the Robot Shield.

.. An assembly video for the board stack will be added here.

Once the kit is assembled, start the first lesson: :doc:`/basic/basic`.
