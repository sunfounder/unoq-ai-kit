# 03 AI Color Light

Show an object to the camera — the AI identifies it and lights an RGB LED in a matching color. Apple → red, banana → yellow, broccoli → green.

![Result](assets/docs_assets/ai_color_light.png)

## Software

### Bricks Used

This example uses the following Bricks:

- `video_object_detection` — Runs the general object-detection model on every camera frame; Python keeps only the classes this project knows how to map to a color
- `web_ui` — Creates the web interface and provides real-time communication between the browser and the Python backend

## Hardware

- Pan Tilt Kit ×1
- Breadboard ×1
- RGB LED (common cathode) ×1
- 220Ω resistor ×3
- Jumper wires
- USB-C cable ×1

## Wiring

Connect the RGB LED's red, green, and blue anodes to **D8**, **D7**, and **D6** — each through a 220Ω resistor — and its common cathode to **GND**.

![Wiring Diagram](assets/docs_assets/wiring_rgb_led.png)

## How to Use the Example

1. Download [`03 AI Color Light.zip`](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/03.AI.Color.Light.zip).
2. In App Lab, go to **Apps** → **Create New App** → **Import App** → **Import from Computer** and open the package you downloaded.
3. Click **Run**.
4. Hold an apple up to the camera — the LED glows red and the Web UI shows the object, its color, and the confidence. Remove the object and the LED turns off after about two seconds.

## Object to Color Mapping

| Object | RGB LED color |
| --- | --- |
| apple | Red |
| banana | Yellow |
| orange | Orange |
| broccoli | Green |
| bottle | Blue |
| person | White |

## How it Works

**Flow**

- Brick (`video_object_detection`) — runs the general model locally and reports every object it recognizes
- Python (`main.py`) — keeps only the mapped classes, picks the most confident one, and calls `Bridge.call("set_color", code)`
- Sketch (`sketch.ino`) — `setColor()` turns that single code into `analogWrite()` levels on D8, D7, and D6
- Python watchdog — switches the LED off after two seconds without a mapped object

**Choosing one object per frame**

The general model reports far more categories than this project needs, so `send_detections()` ignores every class that is not in its mapping table. When several mapped objects share the frame, only the most confident one wins — hold an apple and a banana side by side and the LED follows whichever the model is more sure about.

**One number across the Bridge**

Python never sends three separate brightness values. It sends a single color code, and the sketch's `setColor()` switch turns that code into the right PWM levels. Keeping the protocol small makes the two halves easy to reason about: Python decides *what* the color is, the sketch decides *how* to produce it.

**Turning the LED off again**

A watchdog thread watches the clock. Every mapped detection refreshes it, so the light stays on while the object is visible; if nothing mapped is seen for two seconds the sketch is told to switch the LED off. Note that an unmapped object — a book or a coffee cup — is simply ignored, so the LED goes dark even though the model did recognize something.

The model runs on the UNO Q itself, so no cloud inference is required.
