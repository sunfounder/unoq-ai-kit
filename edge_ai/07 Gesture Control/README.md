# 07 Gesture Control

Show your hand to the camera — the AI recognizes four gestures and controls the hardware:

- 👍 **Thumbs up** (`good`) → RGB LED turns green + the board says *"Great!"*
- ✌️ **V-sign** (`peace`) → the camera takes a photo
- 🖐️ **Open hand** (`five`) → the pan-tilt returns to the center
- ✊ **Fist** (`neut`) → RGB LED off (standby)

## Hardware

- Pan Tilt Kit ×1
- RGB LED (common cathode) ×1
- 220 Ω resistor ×3
- USB-C cable ×1

## Wiring

| Component | UNO Q |
|-----------|-------|
| RGB LED R | D6 (via 220Ω) |
| RGB LED G | D7 (via 220Ω) |
| RGB LED B | D8 (via 220Ω) |
| Pan servo | D9 |
| Tilt servo | D10 |

## Prerequisites

1. App Lab Settings → Carriers → Enable external carriers → Camera → **type1-2lanes** → Reboot.

## How to Use

1. Import `07 Gesture Control.zip` into **Arduino App Lab**.
2. Connect the battery pack to the Robot Shield.
3. Click **Run**.
4. Show your hand to the camera and try each gesture. The Web UI shows the current gesture and the last action, and the board confirms with speech.

## How it Works

- Python (Linux MPU) — the hand-gesture model detects gestures in the camera feed
- The highest-confidence gesture is compared with the previous one — an action runs only when the gesture **changes**
- Thumbs up → `Bridge.call("set_rgb_color", 0, 255, 0)` + TTS "Great!"
- V-sign → `camera.capture()` saves `photos/gesture_001.jpg` + TTS "Cheese!"
- Open hand → `Bridge.call("center_pan_tilt", "")` + TTS "Back to the center."
- Fist → RGB off (no speech)
- When no gesture is seen for 2 seconds, the RGB LED turns off automatically

## Voice Notes

- This project uses **EdgeTTS only** — no STT, no LLM, no API key.
- UNO Q must be connected to the Internet for speech synthesis.
- Speech runs in a background queue so gesture detection stays responsive.
