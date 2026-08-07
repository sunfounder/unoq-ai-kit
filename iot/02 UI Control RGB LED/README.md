# 02 UI Control RGB LED

The **UI Control RGB LED** example demonstrates how to control an RGB LED from a web page using a color picker. Pick any color and the RGB LED lights up in that color — the browser sends RGB values to Python via Socket.IO, Python forwards them to the sketch via Bridge, and the sketch drives the PWM channels on the Robot Shield.

![UI Control RGB LED](assets/docs_assets/rgb_result.png)

## Bricks Used

This example uses the following Brick:

- `web_ui` – Creates the web interface and provides real-time communication between the browser and the Python backend.

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

![Wiring RGB LED](assets/docs_assets/wiring_rgb.png)

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **My Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `02 UI Control RGB LED.zip` from `unoq-ai-kit\iot`.
4. Click **Run**.
5. When the Web UI opens, click the **color preview circle** to open the color picker and choose a color.

## How it Works

The application consists of three parts that work together:

```text
Browser (color picker)
      │
      │ Socket.IO  {r, g, b}
      ▼
Python Backend
      │
      │ Bridge.call("set_rgb_color", r, g, b)
      ▼
Sketch (RobotShield PWM)
      │
      │ P6 (R), P5 (G), P4 (B)
      ▼
RGB LED
```

When a color is picked, the browser sends RGB values (0–255) to Python via Socket.IO. Python calls `Bridge.call("set_rgb_color", r, g, b)` to invoke the sketch function. The sketch maps the 0–255 values to 0–1000 PWM pulses on the Robot Shield channels, setting the RGB LED to the chosen color.

## Code Overview

### Browser

The frontend provides the user interface and handles user interaction.

- `index.html` builds the page layout with a color preview circle.
- `style.css` styles the preview circle and follows the IoT UI design system.
- `app.js` handles the color picker, converts hex ↔ RGB, and sends color updates to the backend.

### Python Backend

`main.py` manages the application logic.

It is responsible for:

- Starting the Web UI server.
- Receiving `{r, g, b}` color values from the browser.
- Calling `Bridge.call("set_rgb_color", r, g, b)` to set the LED color.
- Broadcasting color updates to all connected browsers.

Example:

```python
Bridge.call("set_rgb_color", r, g, b)
```

### Sketch

`sketch.ino` controls the hardware running on the microcontroller.

It:

- Initializes the Robot Shield PWM channels (P4, P5, P6).
- Initializes the Bridge.
- Exposes `set_rgb_color()` for Python to call.
- Maps web-standard 0–255 values to 0–1000 PWM pulses.

Example:

```cpp
Bridge.provide("set_rgb_color", set_rgb_color);

void set_rgb_color(int r, int g, int b) {
    red.setPulse(map(r, 0, 255, 0, 1000));
    green.setPulse(map(g, 0, 255, 0, 1000));
    blue.setPulse(map(b, 0, 255, 0, 1000));
}
```
