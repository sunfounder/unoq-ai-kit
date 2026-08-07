# 01 AI Light Control

Your first AI-powered hardware project. Type a natural-language command — "turn the light red", "make it blue", "switch off" — and an LLM (large language model) translates your words into an RGB LED color.

![AI RGB LED](assets/docs_assets/ai_rgb_result.png)

## What You'll Learn

- How to connect an AI model (OpenAI GPT) to physical hardware
- How the CloudLLM brick sends your words to an LLM and gets a response
- How Bridge passes AI decisions from Python to the Arduino sketch

## Hardware Requirements

### Hardware

- Arduino UNO Q ×1
- Breadboard ×1
- RGB LED (common cathode) ×1
- 220 Ω resistors ×3
- Jumper wires
- USB-C cable ×1

### Software

- Arduino App Lab

## Wiring

Connect the RGB LED through **220 Ω resistors** to the Robot Shield PWM channels:

| RGB LED pin | Robot Shield | Resistor |
|-------------|-------------|----------|
| Red         | P6          | 220 Ω    |
| Green       | P5          | 220 Ω    |
| Blue        | P4          | 220 Ω    |
| GND (common)| GND         | —        |

![Wiring RGB LED](assets/docs_assets/wiring_rgb_led.png)

## How to Use

1. Import `01 AI Light Control.zip` into **Arduino App Lab**.
2. Install the **RobotShield** library if prompted.
3. Click **Run** — App Lab asks for your OpenAI API Key.
4. Enter your key, click Save, then Run again.
5. In the Web UI, type a command like "Turn the light red" and press Send.

## How it Works

```text
Browser (your words)
    │  "Turn the light blue"
    ▼
CloudLLM  ──→  OpenAI GPT
    │              │
    │         returns "blue"
    ▼
Bridge.call("set_color", 3)
    ▼
Sketch — setRgb(0, 0, 1000)
    ▼
RGB LED lights up blue
```

**AI converts natural language into hardware commands.**
