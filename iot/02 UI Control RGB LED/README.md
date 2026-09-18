# 02 UI Control RGB LED

Control an RGB LED from a web page using a color picker. Pick any color and the RGB LED lights up in that color — the browser sends RGB values to Python via Socket.IO, Python forwards them to the sketch via Bridge, and the sketch drives the three PWM channels on the Robot Shield.

## Software

### Bricks Used

- `web_ui` — Creates the web interface and provides real-time communication between the browser and the Python backend

## Hardware

- Arduino UNO Q ×1
- Robot Shield ×1
- Breadboard ×1
- RGB LED (common cathode) ×1
- 220 Ω resistors ×3
- Jumper wires
- USB-C cable ×1

## Wiring

Connect the RGB LED's red, green, and blue anodes through 220 Ω resistors to P6, P5, and P4 on the Robot Shield, and the common cathode to GND.

![Wiring Diagram](assets/docs_assets/wiring_rgb_led.png)

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Download [02 UI Control RGB LED.zip](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/02.UI.Control.RGB.LED.zip) and import it in **Arduino App Lab**.
4. Click **Run**.
5. When the Web UI opens, click the color preview circle to open the color picker and choose a color — the RGB LED lights up in that color.

## How it Works

**Flow**

- Browser — the color picker converts the chosen hex color to 0–255 R/G/B values and sends them through Socket.IO
- Python (`main.py`) — receives the values and calls `Bridge.call("set_rgb_color", r, g, b)`
- Sketch (`sketch.ino`) — maps 0–255 values to 0–1000 PWM pulses and sets them on the Robot Shield's P4, P5, P6 channels
- The sketch's `loop()` is empty — everything is event-driven through Bridge

**The PWM mapping**

Web colors use 0–255 per channel, but the Robot Shield's PWM range is 0–1000. The sketch calls `map(r, 0, 255, 0, 1000)` for each channel, so a web-standard `(255, 0, 0)` becomes full-brightness red.

**Three channels, one color**

Each PWM channel (P6 red, P5 green, P4 blue) controls the brightness of one primary color. `set_rgb_color(r, g, b)` sets all three pulse widths in one call, so the LED appears as a single mixed color rather than three separate lights.
