.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

Module A: Basic Interaction
===============================

In this module, you'll explore the fundamentals of hardware control using the Arduino UNO Q and a breadboard — **no Python, no web UI, just Arduino sketches running on the STM32 microcontroller**. Through 15 hands-on experiments, you'll go from blinking an LED to reading a 10-axis IMU over I2C.

Each lesson introduces at most one genuinely new concept. Everything else builds on what you already know, so you can focus on the one new thing each time.

By the end of this module, you will be able to:

* Wire components on a breadboard and read circuit diagrams
* Use digital and analog I/O to control LEDs, buzzers, and motors
* Read sensors — light, temperature, distance, motion
* Control servos and DC motors with the Robot Shield
* Communicate with complex sensors over I2C

.. toctree::
   :maxdepth: 1

   1_hello_led
   2_button_led
   3_tilt_alarm
   4_photoresistor_led
   5_potentiometer_buzzer
   6_rgb_led
   7_motor
   8_servo
   9_ultrasonic
   10_dht11
   11_imu
   12_thermistor_fan
   13_joystick_servo
   14_imu_servo

