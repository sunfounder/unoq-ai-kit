# 16 LED Matrix Patterns

Display five simple icons — heart, star, smile, arrow, and check mark — on the UNO Q's built-in 8×13 LED matrix. Each pattern is stored as a bitmap of 0s and 1s in a separate header file, making the sketch clean and the patterns easy to modify.

## Hardware

- Arduino UNO Q ×1
- USB-C cable ×1

## Wiring

No breadboard wiring is needed. The LED matrix is built into the UNO Q board.

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Download [16 LED Matrix Patterns.zip](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/16.LED.Matrix.Patterns.zip) and import it in **Arduino App Lab**.
4. Click **Run**.
5. Five patterns cycle continuously on the LED matrix — one second per pattern.

## How it Works

**Flow**

- `setup()` — initializes the LED matrix with `matrix.begin()` and clears it
- `loop()` — calls `showPattern()` for each of the five patterns, cycling through them forever

**The LED matrix**

`Arduino_LED_Matrix matrix` creates an object for the built-in 8-row × 13-column LED grid. `matrix.begin()` initializes the hardware, and `matrix.renderBitmap(pattern, 8, 13)` writes a pattern to the grid — each `1` lights an LED, each `0` keeps it off.

**The patterns**

All five patterns live in `matrix_patterns.h` as `uint8_t[8][13]` arrays — 8 rows of 13 columns. `showPattern()` is a helper that takes a pattern array, calls `renderBitmap()` to display it, and holds it for one second. Separating patterns from logic means you can edit the icons without touching the main sketch.
