# 03 AI Color Light

Show an object to the camera — the AI identifies it and lights up the RGB LED in a matching color. Apple → red, banana → yellow, broccoli → green. Each detected object maps to a color via Bridge.

![Result](assets/docs_assets/rgb_result.png)

## Hardware

- Pan Tilt Kit ×1
- RGB LED (common cathode) ×1
- 220 Ω resistor ×3
- USB-C cable ×1

## Wiring

| RGB LED pin | UNO Q |
|-------------|-------|
| Red anode   | D8 (via 220Ω) |
| Green anode | D7 (via 220Ω) |
| Blue anode  | D6 (via 220Ω) |
| Common cathode | GND |

![Wiring](assets/docs_assets/wiring_rgb_led.png)

## Object → Color Mapping

| Object | RGB LED Color |
|--------|--------------|
| apple | Red |
| banana | Yellow |
| orange | Orange |
| broccoli | Green |
| bottle | Blue |
| person | White |

## Prerequisites

1. App Lab Settings → Carriers → Enable external carriers → Camera → **type1-2lanes** → Reboot.

## How to Use

1. Import `03 AI Color Light.zip` into **Arduino App Lab**.
2. Click **Run**.
3. Show a supported object to the camera — the RGB LED changes to its mapped color. When no object is detected for 2 seconds, the LED turns off.

## How it Works

- CSI Camera → video object detection brick (general model)
- Video stream → Web UI
- Detection → Python maps the object to a color code
- `Bridge.call("set_color", code)` → the sketch sets the RGB LED with `analogWrite()` on D8/D7/D6

The AI model runs locally on the UNO Q. No cloud inference required.
