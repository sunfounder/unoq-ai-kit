# 05 Voice Command

The **Voice Command** example puts local speech recognition to work: hold the button, say a color command such as "Turn on the red light.", release the button, and the RGB LED changes color through keyword matching and Bridge.

## Software

### Bricks Used

This example uses the following Bricks:

- `robot_shield` — Provides access to the Robot Shield hardware (I2C, GPIO, audio, PWM)
- `sunfounder_stt` — Local speech-to-text engine (Whisper model)

### Libraries Used

- **RobotShield** library (install via Library Manager)
- **SunFounder_STT** library (install via Library Manager)

## Hardware

- Arduino UNO Q ×1
- Robot Shield ×1
- Multimedia Carrier ×1
- RGB LED module ×1
- Push button ×1
- Breadboard ×1
- Jumper wires
- USB-C cable ×1

## Wiring

### Push Button

- Button pin 1 → **D2**
- Button pin 2 → **GND**

### RGB LED

- R → **P6**
- G → **P5**
- B → **P4**

Connect the RGB LED ground pin to GND when required by your module.

![Wiring Diagram](assets/docs_assets/wiring_button_rgb.png)

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **My Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `05 Voice Command.zip` from `unoq-ai-kit\media`.
4. Click **Run**.
5. When the app starts, the RGB LED flashes red → green → blue → off as a wiring test. Then wait for `Local STT is ready.`, hold the button and say a color command (for example, "Turn on the blue light."), and release the button — the RGB LED changes color and `Light set to blue.` appears in the **Output** window.

Supported commands: `red`, `green`, `blue`, `yellow`, `cyan`, `purple`, `white`, and `off` — as single words or inside a full sentence.

## How it Works

```text
Button pressed → start recording
    ↓
Button released → stop recording
    ↓
stt.get_result() → "Turn on the blue light."
    ↓
Keyword match → "blue" found in SUPPORTED_COLORS
    ↓
Bridge.call("set_color", "blue") → sketch sets PWM
    ↓
RGB LED glows blue
```

- The recognized text is converted to lowercase and searched for color keywords, so a single word (`blue`) and a full sentence (`Turn on the blue light.`) both work.
- `off` is checked first, so saying "Turn off the light." turns the LED off.
- Python only sends the color name over Bridge; the sketch decides the exact PWM values for each color.

## Code Overview

### Python

`python/main.py` runs on the Linux MPU.

```python
import time

from arduino.app_utils import Bridge
from sunfounder_stt import STT

BUTTON_RPC = "button_read"
COLOR_RPC = "set_color"
POLL_INTERVAL = 0.05
MIN_RECORDING_TIME = 0.5

SUPPORTED_COLORS = (
    "red",
    "green",
    "blue",
    "yellow",
    "cyan",
    "purple",
    "white",
)

print("Preparing the audio input...", flush=True)
stt = STT(type="local_fast", language="en")

print("Local STT is ready.", flush=True)
print("Say a color, or say 'turn off the light'.", flush=True)
print("Hold the button and speak. Release it to recognize.", flush=True)

last_state = 0
recording = False
recording_started_at = 0.0

while True:
    state = int(Bridge.call(BUTTON_RPC, ""))

    if state == 1 and last_state == 0 and not recording:
        print("\nListening...", flush=True)
        stt.start_listening()
        recording = True
        recording_started_at = time.monotonic()

    elif state == 0 and last_state == 1 and recording:
        recording_time = time.monotonic() - recording_started_at

        if recording_time < MIN_RECORDING_TIME:
            time.sleep(MIN_RECORDING_TIME - recording_time)

        print("Recognizing...", flush=True)
        stt.stop_listening()
        text = stt.get_result()

        if text and text.strip():
            command = text.strip().lower()
            print(f"You said: {text.strip()}", flush=True)

            selected_color = None

            if "off" in command:
                selected_color = "off"
            else:
                for color in SUPPORTED_COLORS:
                    if color in command:
                        selected_color = color
                        break

            if selected_color is None:
                print(
                    "Try: red, green, blue, yellow, cyan, purple, white, or off.",
                    flush=True,
                )
            else:
                Bridge.call(COLOR_RPC, selected_color)

                if selected_color == "off":
                    print("Light turned off.", flush=True)
                else:
                    print(f"Light set to {selected_color}.", flush=True)

        recording = False

    last_state = state
    time.sleep(POLL_INTERVAL)
```

- `SUPPORTED_COLORS` — The tuple of color keywords the program understands.
- `if "off" in command` / `for color in SUPPORTED_COLORS` — Searches the recognized text for a keyword; sentences like "Turn on the red light." still match.
- `Bridge.call(COLOR_RPC, selected_color)` — Sends the color name to the sketch, which sets the RGB LED accordingly.

### Sketch

`sketch/sketch.ino` runs on the STM32 MCU.

```cpp
#include "RobotShield.h"
#include <Arduino_RouterBridge.h>

const int BUTTON_PIN = 2;

Pwm redLed(6);
Pwm greenLed(5);
Pwm blueLed(4);

void setRgb(uint16_t red, uint16_t green, uint16_t blue)
{
    redLed.setPulse(red);
    greenLed.setPulse(green);
    blueLed.setPulse(blue);
}

void setColor(String color)
{
    String selectedColor = color;
    selectedColor.toLowerCase();

    if (selectedColor == "red") {
        setRgb(1000, 0, 0);
    } else if (selectedColor == "green") {
        setRgb(0, 1000, 0);
    } else if (selectedColor == "blue") {
        setRgb(0, 0, 1000);
    } else if (selectedColor == "yellow") {
        setRgb(1000, 700, 0);
    } else if (selectedColor == "cyan") {
        setRgb(0, 1000, 1000);
    } else if (selectedColor == "purple") {
        setRgb(500, 0, 700);
    } else if (selectedColor == "white") {
        setRgb(1000, 1000, 1000);
    } else {
        setRgb(0, 0, 0);
    }
}

int buttonRead(String dummy)
{
    (void)dummy;
    return digitalRead(BUTTON_PIN) == LOW ? 1 : 0;
}

void setup()
{
    pinMode(BUTTON_PIN, INPUT_PULLUP);

    I2cBus::i2c().begin();

    redLed.begin();
    greenLed.begin();
    blueLed.begin();

    redLed.setFreq(1000);
    greenLed.setFreq(1000);
    blueLed.setFreq(1000);

    redLed.setEnable(true);
    greenLed.setEnable(true);
    blueLed.setEnable(true);

    // Startup test: red -> green -> blue.
    setRgb(1000, 0, 0);
    delay(500);
    setRgb(0, 1000, 0);
    delay(500);
    setRgb(0, 0, 1000);
    delay(500);
    setRgb(0, 0, 0);

    Bridge.begin();
    Bridge.provide("button_read", buttonRead);
    Bridge.provide("set_color", setColor);
}

void loop()
{
    delay(10);
}
```

- `Pwm redLed(6)` — Creates a PWM output on port P6 for the red channel.
- `setRgb(red, green, blue)` — Sets all three channels at once; each value ranges from 0 to 1000.
- The startup test flashes red → green → blue → off so you can verify the LED wiring before testing voice commands.
- `Bridge.provide("set_color", setColor)` — Registers the function so Python can change the color.
