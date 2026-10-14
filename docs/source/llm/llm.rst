.. include:: /index.rst
   :start-after: start_hello_message
   :end-before: end_hello_message

Module E: AI & Large Language Models
====================================

In this module, you'll connect your UNO Q to **large language models** (LLMs) like OpenAI's GPT. Instead of writing code to control every detail of your hardware, you'll describe what you want in natural language — and the AI will figure out the rest.

Using the **CloudLLM** brick in App Lab, your Python code can send user messages to an LLM, receive intelligent responses, and translate those responses into hardware commands via Bridge. This is the essence of AIoT: the bridge between human language and physical devices.

This module covers:

* **LLM Integration**: Connect your UNO Q to GPT-4o-mini via the CloudLLM brick
* **Natural Language Control**: Control RGB LEDs, servos, and sensors by describing what you want
* **Prompt Engineering**: Write system prompts that make the LLM behave reliably as a hardware controller
* **Context-Aware Control**: Combine what you say with what the room is actually doing — temperature, humidity, movement — and let the model answer with light

By the end of this module, you will be able to:

* Configure an API key and connect an LLM to your hardware
* Write prompts that translate natural language into hardware commands
* Build AI-powered devices that understand and respond to human speech
* Describe a behaviour in a prompt — like turning a mood into a colour — instead of writing it as rules in code

Let's give your UNO Q a mind.


.. _llm_other_models:

Using another online model
--------------------------

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

.. toctree::
   :maxdepth: 1

   01_ai_light_control
   02_ai_digital_pet
   03_ai_environment_advisor
   04_ai_voice_assistant
   05_ai_vision_assistant
   06_ai_scavenger_hunt
   07_ai_quiz_show
   08_ai_story_dice
   09_ai_show_and_tell
   10_ai_context_aware_room_assistant


