# 03 AI Voice Vision Assistant V7

This version is built from the two verified working examples:

- `02 AI Voice Assistant`
- `01 AI Camera Basics`

## Features

- Smooth live camera preview through the official `VideoObjectDetection` stream service
- Camera ON/OFF display button in the Web UI
- Working Voice Assistant STT configuration: `tiny` model and English language
- CloudLLM conversation
- Cloud vision when the user asks a visual question such as “What do you see?”
- EdgeTTS spoken response
- External LED on D5 controlled only by voice

## How visual questions work

The live camera stays visible in the browser. When the user asks a visual question, the app captures the current camera frame and sends it to CloudLLM Vision. From the learner’s perspective, the assistant is watching the live camera and answering about what it sees.

## Example commands

```text
What do you see?
Can you see a person?
Turn on the LED.
Turn off the LED.
```

## LED wiring

```text
LED anode   -> D5 through a current-limiting resistor
LED cathode -> GND
```
