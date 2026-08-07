# 06 Color Mixer

Cycle an RGB LED through 8 colors using three independent PWM channels. Each color channel (Red, Green, Blue) gets its own PWM control — by mixing different brightness levels of the three primary colors, you can create any color. The RobotShield library manages all three PWM channels simultaneously.



## Libraries Used

- **RobotShield** library


## Hardware

- Pan Tilt Kit ×1
- Breadboard ×1
- RGB LED (common cathode) ×1
- 220 Ω resistors ×3
- Jumper wires
- USB-C cable ×1


## Wiring

Connect the RGB LED's red, green, and blue anodes through 220 Ω resistors to P6, P5, and P4, and the common cathode to GND.

![Wiring Diagram](assets/docs_assets/wiring_rgb_led.png)

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **My Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `06 Color Mixer.zip` from `unoq-ai-kit\basic`.
5. Click **Run**.
6. The RGB LED cycles through Red, Green, Blue, Yellow, Cyan, Magenta, White, and Off — one second per color.

## How it Works

**Flow**

- `setup()` — initializes the I2C bus, sets all three PWM channels to 1000 Hz, and enables their outputs
- `loop()` — calls `setColor()` with different R/G/B values, pausing one second per color

**Three channels, one color**

Each PWM channel (P6 red, P5 green, P4 blue) controls the brightness of one primary color with a pulse width from 0 (off) to 1000 (full brightness). `setColor(r, g, b)` sets all three pulse widths in one call, so the LED appears as a single mixed color rather than three separate lights.

**The 8-color cycle**

Yellow = red + green, cyan = green + blue, magenta = red + blue, and white = all three at full brightness. The `loop()` walks through all eight combinations — including off — one second per color, then repeats.

