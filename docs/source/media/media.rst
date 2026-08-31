.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

Module B: Multimedia (Python and Sketch)
==========================================

In Module A, your outputs were LEDs and buzzers, and your inputs were switches and sensors. Now you'll work with the **Multimedia Carrier** — the expansion board with a **speaker**, **microphone**, and **camera** built in. No breadboard, no wiring: everything is already attached to your UNO Q.

In this module, you'll learn to:

* Make the speaker talk with text-to-speech (TTS)
* Turn your voice into text with speech-to-text (STT)
* Capture photos and video with the camera
* Combine voice commands with hardware control

Let's give your UNO Q ears, a voice, and eyes.

.. note::

   The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

.. toctree::
   :maxdepth: 1

   1_local_tts
   2_dynamic_tts
   3_voice_recorder
   4_local_stt
   5_voice_rgb_led
   6_stt_echo
   7_voice_pan_tilt
   8_camera_snapshot
   9_voice_camera
