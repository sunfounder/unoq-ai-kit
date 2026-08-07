.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

Module B: UI / Arduino Cloud / IoT
=======================================

In Module A, your UNO Q controlled hardware locally — all the sensing and actuation happened right on your desk. In this module, you'll connect your device to the **internet** and build applications that bridge the physical and digital worlds.

Using **Arduino App Lab's UI builder** and **Arduino Cloud**, you'll create web dashboards, remote controls, and even a Telegram bot that can interact with your hardware from anywhere in the world. Press a button on a webpage and an LED lights up on your desk. Upload sensor data to the cloud and view it as charts. Send a message from your phone and your buzzer beeps.

This module covers the full IoT stack:

* **Local UI**: Build web buttons, sliders, and displays in App Lab that control hardware in real time
* **Cloud Data**: Upload sensor readings to Arduino Cloud and visualize them as dashboards
* **Remote Control**: Use Arduino Cloud to control your device from anywhere with internet access
* **External Services**: Connect Telegram, webhooks, and other services to your hardware

By the end of this module, you will be able to:

* Design web-based control interfaces using App Lab's UI builder
* Upload sensor data to Arduino Cloud and create live dashboards
* Control your UNO Q remotely from a web browser or mobile device
* Integrate third-party services (Telegram) with your hardware

Let's take your projects online.

.. toctree::
   :maxdepth: 1

   1_ui_led
   2_ui_rgb_led
   3_cloud_buzzer
   4_cloud_environment
   5_web_game
   6_climate_dashboard
   7_telegram_bot
