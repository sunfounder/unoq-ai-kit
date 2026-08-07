# 03 Face Tracking Camera with TTS

The pan servo scans from side to side (−45° to +45°). When the camera detects a face, the servo stops and plays the greeting `Hello, nice to meet you.` If the face disappears for 2.5 seconds, scanning resumes automatically. This is the first project where AI controls physical movement — not just ON/OFF but continuous tracking behavior.

![Result](assets/docs_assets/tracking_result.png)

## Hardware Requirements

### Hardware

- Arduino UNO Q ×1
- Robot Shield (stacked on UNO Q)
- Multimedia Carrier with CSI camera
- Pan servo (connected to servo channel 0)
- Tilt servo (connected to servo channel 1)
- Battery pack ×1
- USB-C cable ×1

### Software

- Arduino App Lab
- RobotShield library (install via Library Manager)
- `sunfounder_tts` Python package
- Internet connection for EdgeTTS

## Wiring

| Component | Robot Shield |
|-----------|-------------|
| Pan servo | Servo channel 0 |
| Tilt servo | Servo channel 1 |
| Battery | Battery connector |

![Wiring](assets/docs_assets/wiring_imu_servo.png)

## Behavior

1. The pan servo scans from −45° to +45°.
2. The tilt servo stays at 0°.
3. Camera feed and face bounding box shown in Web UI.
4. When a face is detected, the pan servo **stops**.
5. When a new face appears, EdgeTTS plays **Hello, nice to meet you.**
6. If no face is detected for 2.5 seconds, scanning **resumes**.

## Prerequisites

1. Open App Lab settings → enable external carrier → Camera → `type1-2lanes` → Reboot.

## How to Use

1. Import `03 Face Tracking Camera.zip` into **Arduino App Lab**.
2. Install **RobotShield** library if prompted.
3. Connect the battery pack.
4. Click **Run**.
5. Stand in front of the camera — the servo stops and the speaker plays `Hello, nice to meet you.` Step away — after 2.5 seconds scanning resumes.

## How it Works

```text
Sketch (STM32 MCU)              Python (Linux MPU)
    │                               │
    │  servo sweep loop             │  face detection brick
    │  Bridge.provide(stop/start)   │  on_detect("face") → stop_scanning
    │                               │  bg thread → timeout 2.5s → start_scanning
    │                               │
    └──────── Bridge I2C ───────────┘
```

- **Sketch** runs the servo sweep autonomously. It exposes `stop_scanning()` and `start_scanning()` via Bridge.
- **Python** monitors face detection. When `face_detected()` fires, it calls `Bridge.call("stop_scanning")`.
- A **background thread** checks every 200ms whether the face has been gone for ≥ 2.5 seconds — if so, it calls `Bridge.call("start_scanning")` to resume.


## Voice Notes

- This project uses **EdgeTTS only**.
- It does not use STT, CloudLLM, Gemini, OpenAI, or Claude.
- No API key is required.
- UNO Q must be connected to the Internet for speech synthesis.
- The greeting is queued in a background thread so the camera and face detection remain responsive.


## EdgeTTS output directory

`sunfounder_tts.EdgeTTS` saves its temporary MP3 file to
`./audio_output/edge_tts.mp3`. The application creates both
`./audio_output` and `/app/audio_output` automatically before playback.
