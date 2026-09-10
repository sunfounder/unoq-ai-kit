# 05 Face Tracking Camera

When the camera sees a face, the board greets **"Nice to meet you."** and starts following it in two directions. The pan servo turns left and right, while the tilt servo moves up and down to keep the face centered. When the face disappears for 2.5 seconds, both servos return to the center.

![Result](assets/docs_assets/tracking_result.png)

## Hardware

- Pan Tilt Kit ×1
- USB-C cable ×1

## Wiring

| Component | UNO Q |
|-----------|-------|
| Pan servo | D9 |
| Tilt servo | D10 |

![Wiring](assets/docs_assets/wiring_imu_servo.png)

## Behavior

1. The pan-tilt starts at the 90° center.
2. When a face is detected for the first time, EdgeTTS plays **Nice to meet you.**
3. The pan servo follows horizontal movement and the tilt servo follows vertical movement.
4. Each servo moves 1° per tracking step and ignores offsets within the 10% dead zone.
5. If no face is detected for 2.5 seconds, the pan-tilt returns to the center and the next face triggers a new greeting.

## Prerequisites

1. Open App Lab settings → enable external carrier → Camera → `type1-2lanes` → Reboot.

## How to Use

1. Import `05 Face Tracking Camera.zip` into **Arduino App Lab**.
2. Connect the battery pack to the Robot Shield.
3. Click **Run**.
4. Stand in front of the camera — the board says *"Nice to meet you."* Move left, right, up, and down slowly so the camera can follow you. Step away — after 2.5 seconds both servos return to 90°.

## How it Works

- Python (Linux MPU) — the face-detection brick finds faces and reports each detection box
- Python reads App Lab's `bounding_box_xyxy` coordinates and computes the horizontal and vertical center
- Outside the dead zone → `Bridge.call("pan_step", direction)` and/or `Bridge.call("tilt_step", direction)`
- Sketch (STM32 MCU) moves each servo by 1° per call
- Pan is clamped to 45°–135°; tilt is clamped to 45°–115°
- A background thread watches for the face-loss timeout and calls `center_pan_tilt` to return to 90°

## Voice Notes

- This project uses **EdgeTTS only**.
- It does not use STT, CloudLLM, Gemini, OpenAI, or Claude.
- No API key is required.
- The project includes the complete `sunfounder_tts` custom Brick.
- UNO Q must be connected to the Internet for EdgeTTS.
- The greeting is queued in a background thread so the camera and face detection remain responsive.

> **First TTS run:** App Lab may need half an hour or more to download and prepare the TTS runtime and audio dependencies. Keep the board connected to the Internet. This setup normally happens only once.
