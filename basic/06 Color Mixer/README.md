# 06 Color Mixer

Cycle an RGB LED through 8 colors using three PWM pins and `analogWrite()`. Each color channel (Red, Green, Blue) gets its own PWM control — by mixing different brightness levels of the three primary colors, you can create any color.

## Hardware

- Pan Tilt Kit ×1
- Breadboard ×1
- RGB LED (common cathode) ×1
- 220 Ω resistors ×3
- Jumper wires
- USB-C cable ×1

## Wiring

Connect the RGB LED's red, green, and blue anodes through 220 Ω resistors to D8, D7, and D6, and the common cathode to GND.

![Wiring Diagram](assets/docs_assets/wiring_rgb_led.png)

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Download [06 Color Mixer.zip](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/06.Color.Mixer.zip) and import it in **Arduino App Lab**.
4. Click **Run**.
5. The RGB LED cycles through Red, Green, Blue, Yellow, Cyan, Magenta, White, and Off — one second per color.

## How it Works

**Flow**

- `setup()` — configures all three LED pins as outputs
- `loop()` — calls `setColor()` with different R/G/B values, pausing one second per color

**Three pins, one color**

Each pin (D8 red, D7 green, D6 blue) controls the brightness of one primary color with `analogWrite()` — a value from 0 (off) to 255 (full brightness). `setColor(r, g, b)` sets all three in one call, so the LED appears as a single mixed color rather than three separate lights.

**The 8-color cycle**

Yellow = red + green, cyan = green + blue, magenta = red + blue, and white = all three at full brightness. The `loop()` walks through all eight combinations — including off — one second per color, then repeats.
