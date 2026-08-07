.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

FAQ
===============

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

当你导入一个.zip的文件，你如果看到Sketch Libraries有提示这个APP用到的库。


或者当你运行时，显示报错 ``fatal error: xxxx.h: No such file or directory``

你可以去安装或更新对应的库。现在参考下面两个步骤。

#. 点击**Add Sketch Library**

   .. image:: img/faq_add_lib_c.png

#. 搜索文档上提示的库的比如，比如RobotShield

   .. image:: img/faq_install_lib_c.png



Note: To ensure the UNO Q board is properly detected by the Arduino App Lab, your user account must have specific write permissions for the USB device. Without these permissions, the board may not appear in the application or allow connections. Please refer to the Linux Host Setup section in the UNO Q User Manual to install the necessary udev rules.

https://docs.arduino.cc/tutorials/uno-q/user-manual/#linux-host-setup-required-for-linux-users



Flashing a New Image to the UNO Q
-------------------------------------------


需要短接2个引脚，然后插入UNO Q

<此处需要配张图>

.. https://docs.arduino.cc/tutorials/uno-q/update-image/

.. Download the Arduino Flasher CLI for your OS (MacOS / Linux / Windows)：https://www.arduino.cc/en/software/#flasher-tool


.. Unzip the downloaded file, (you will receive an executable binary named arduino-flasher-cli)


.. Navigate to the unzipped folder (e.g. arduino-flasher-cli-x.x.x-windows-amd64), and run the following command:

.. windows运行下面的命令


.. ./arduino-flasher-cli.exe flash latest

