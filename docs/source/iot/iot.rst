.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

Module C: UI / Arduino Cloud / IoT
=======================================

In Module A, you controlled hardware with sketches — LEDs, sensors, servos, and motors, all running locally on your desk. In Module B, you explored the AVIO Carrier's built-in **speaker**, **microphone**, and **camera**. Now you'll connect your device to the **internet** and build applications that bridge the physical and digital worlds.

Using **Arduino App Lab's UI builder**, **Arduino Cloud**, and **Telegram**, you'll create web dashboards, remote controls, games, security systems, and even a chat bot that can interact with your hardware from anywhere in the world. Press a button on a webpage and an LED lights up on your desk. Watch sensor data flow into a live chart. Upload readings to the cloud and view them as dashboards. Send a message from your phone and your LED turns on.

This module covers the full IoT stack:

* **Local UI**: Build web buttons, color pickers, and displays in App Lab that control hardware in real time
* **Hardware to Browser**: Stream sensor readings and joystick input into live charts and browser games
* **Cloud Data**: Upload sensor readings to Arduino Cloud and visualize them as dashboards
* **Remote Control**: Use Arduino Cloud to control your device from anywhere with internet access
* **Camera and Events**: Build a smart doorbell and a security monitor with live camera previews
* **External Services**: Connect Telegram and other services to your hardware

By the end of this module, you will be able to:

* Design web-based control interfaces using App Lab's UI builder
* Stream sensor data to the browser and visualize it in real time
* Upload sensor data to Arduino Cloud and create live dashboards
* Control your UNO Q remotely from a web browser or mobile device
* Combine cameras, sensors, and events into practical IoT applications
* Integrate third-party services (Telegram) with your hardware

Let's take your projects online.

.. toctree::
   :maxdepth: 1

   01_ui_led
   02_ui_rgb_led
   03_sensor_data_dashboard
   04_ui_joystick_maze
   05_voice_announcer
   06_cloud_melody_pitch
   07_cloud_environment
   08_smart_doorbell
   09_iot_security_monitor
   10_voice_message
   11_telegram_bot
   12_iot_smart_room
