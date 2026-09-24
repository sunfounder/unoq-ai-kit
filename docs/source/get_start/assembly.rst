.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

Assembly
============

Put the kit together before starting the lessons. There are two parts: the **board stack** and the **pan-tilt mount**.

**Board Stack: UNO Q + Robot Shield + AVIO Carrier**

The three boards are designed to stack on top of each other.

#. The **Robot Shield** goes on top of the **UNO Q**. Line up its headers with the UNO Q's pins and press it down firmly until every pin is fully seated.
#. The **AVIO Carrier** plugs into the UNO Q's high-speed connectors. Line up its two sockets with the matching connectors and press it down until it is fully seated.
#. If you are using a battery, connect it to the battery terminal on the Robot Shield — see :doc:`robot_shield`.

.. An assembly video for the board stack will be added here.

**Pan-Tilt Mount**

The pan-tilt mount carries the camera and lets the two servos aim it.

#. Mount the **pan servo** on the base of the mount.
#. Mount the **tilt servo** and the camera bracket on top of the pan section.
#. Attach the **camera** to the tilt bracket and connect its FPC cable to the AVIO Carrier — see :doc:`avio_carrier`.
#. Plug the pan servo into **D9** and the tilt servo into **D10** on the Robot Shield.

.. A step-by-step video for the pan-tilt assembly will be added here.

Once the kit is assembled, continue with :doc:`app_lab` to install Arduino App Lab.
