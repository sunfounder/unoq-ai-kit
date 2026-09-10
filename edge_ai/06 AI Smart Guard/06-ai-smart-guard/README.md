# 06 AI Smart Guard

A complete security system. The camera scans for intruders — when a **person** (full body, not just a face) is detected, the RGB LED turns red, the buzzer sounds, the scanning servo stops, and a voice alert plays. After 3 seconds of no detection, it returns to green "all clear" mode.

This is the capstone project: every skill from lessons 01–05 combined into one system.

![Result](assets/docs_assets/guard_result.png)

## Hardware Requirements

### Hardware

- Arduino UNO Q ×1
- Multimedia Carrier with CSI camera
- RGB LED (common cathode) ×1
- 220 Ω resistors ×3
- Active buzzer ×1
- Pan Tilt Kit ×1
- USB-C cable ×1

### Software

- Arduino App Lab
- Arduino_HardwareServo library

## Person Detection vs Face Detection

This project uses **general object detection** — it looks for a person's entire body, not just their face. Unlike lessons 03 and 04 (which require a clear face view), person detection works even when someone is facing away, wearing a mask, or partially obscured.

| | Face Detection (03/04) | Person Detection (06) |
|---|---|---|
| Model | `model: face-detection` | General model |
| Back to camera | ❌ Not detected | ✅ Detected |
| Mask/sunglasses | ⚠️ May miss | ✅ Unaffected |
| Use case | Greeting, face tracking | Security, crowd counting |

## Wiring

| Component | UNO Q |
|-----------|-------|
| RGB LED Red anode | D8 (via 220Ω) |
| RGB LED Green anode | D7 (via 220Ω) |
| RGB LED Blue anode | D6 (via 220Ω) |
| RGB LED Common cathode | GND |
| Buzzer (+) | D5 |
| Buzzer (−) | GND |
| Pan servo signal | D9 |
| Tilt servo signal | D10 |
| Servo power | 5V and GND |

## Behavior

| State | Servo | RGB LED | Buzzer | Voice |
|-------|-------|---------|--------|-------|
| All clear | Scanning left/right | 🟢 Green | Silent | — |
| Person detected | Stops scanning | 🔴 Red | Beeping alarm | "Intruder detected" |
| Person lost (3s) | Resumes scanning | 🟢 Green | Silent | "All clear" |

## Prerequisites

1. App Lab Settings → Carriers → Enable external carriers → Camera → **type1-2lanes** → Reboot.

## How to Use

1. Import `06 AI Smart Guard.zip` into **Arduino App Lab**.
2. Click **Run**.
3. The servo scans and RGB glows green. Walk in front of the camera — the alarm triggers with red light, beeping, and voice alert. Step away for 3 seconds — it returns to green.

## How it Works

- CSI Camera → VideoObjectDetection (general model)
- Video stream → Web UI
- `on_detect_all()` → "person" found?
- YES → `Bridge.call("alarm_on")` → Sketch: red LED + buzzer + stop scan; Python: EdgeTTS speaks alert
- NO → monitor thread checks timeout → 3s elapsed? → `Bridge.call("alarm_off")` → Sketch: green LED + silent + resume scan

- **Sketch** handles all three outputs (servo, RGB LED, buzzer) in the same file. Two Bridge commands `alarm_on()` and `alarm_off()` toggle between states.
- **Python** uses the general `VideoObjectDetection` brick (no `model: face-detection`), so it detects full bodies. The `on_detect_all` callback checks for "person" among the detected classes.
- **EdgeTTS** runs in a background thread so voice announcements never block face detection.

> **First TTS run:** App Lab may need half an hour or more to download and prepare the TTS runtime and audio dependencies. Keep the board connected to the Internet. This setup normally happens only once.
