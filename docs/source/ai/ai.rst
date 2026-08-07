.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

Module C: AI & Large Language Models
========================================

In this module, you'll connect your UNO Q to **large language models** (LLMs) like OpenAI's GPT. Instead of writing code to control every detail of your hardware, you'll describe what you want in natural language — and the AI will figure out the rest.

Using the **CloudLLM** brick in App Lab, your Python code can send user messages to an LLM, receive intelligent responses, and translate those responses into hardware commands via Bridge. This is the essence of AIoT: the bridge between human language and physical devices.

This module covers:

* **LLM Integration**: Connect your UNO Q to GPT-4o-mini via the CloudLLM brick
* **Natural Language Control**: Control RGB LEDs, servos, and sensors by describing what you want
* **Prompt Engineering**: Write system prompts that make the LLM behave reliably as a hardware controller

By the end of this module, you will be able to:

* Configure an API key and connect an LLM to your hardware
* Write prompts that translate natural language into hardware commands
* Build AI-powered devices that understand and respond to human speech

Let's give your UNO Q a mind.

.. toctree::
   :maxdepth: 1

   1_ai_light_control
