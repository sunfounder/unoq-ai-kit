# 05 Voice-Controlled RGB LED

The **Voice-Controlled RGB LED** example puts local speech recognition to work: hold the button, say a color command such as "Turn on the red light.", release the button, and the RGB LED changes color through keyword matching and Bridge.

## Software

### Bricks Used

This example uses the following Bricks:

- `sunfounder_stt` — Local speech-to-text engine (Whisper model)

## Hardware

- Pan Tilt Kit ×1
- RGB LED ×1
- 220Ω resistor ×3
- Push button ×1
- Breadboard ×1
- Jumper wires
- USB-C cable ×1

## Wiring

### Push Button

- Button pin 1 → **D4**
- Button pin 2 → **GND**

### RGB LED

- R → 220Ω resistor → **D8**
- G → 220Ω resistor → **D7**
- B → 220Ω resistor → **D6**

Connect the RGB LED ground pin to GND when required by your module.

![Wiring Diagram](assets/docs_assets/wiring_button_rgb.png)

## How to Use the Example

1. Download [`05 Voice-Controlled RGB LED.zip`](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/05.Voice-Controlled.RGB.LED.zip).
2. In App Lab, go to **Apps** → **Create New App** → **Import App** → **Import from Computer** and open the package you downloaded.
3. Click **Run**.
4. When the app starts, the RGB LED flashes red → green → blue → off as a wiring test. Then wait for `Local STT is ready.`, hold the button and say a color command (for example, "Turn on the blue light."), and release the button — the RGB LED changes color and `Light set to blue.` appears in the **Output** window.

Supported commands: `red`, `green`, `blue`, `yellow`, `cyan`, `purple`, `white`, and `off` — as single words or inside a full sentence.

## How it Works

- Button pressed → starts recording
- Button released → stops recording
- `stt.get_result()` → "Turn on the blue light."
- Keyword match → "blue" found in `SUPPORTED_COLORS`
- `Bridge.call("set_color", "blue")` → the sketch sets PWM
- The RGB LED glows blue

- The recognized text is converted to lowercase and searched for color keywords, so a single word (`blue`) and a full sentence (`Turn on the blue light.`) both work.
- `off` is checked first, so saying "Turn off the light." turns the LED off.
- Python only sends the color name over Bridge; the sketch decides the exact PWM values for each color.
