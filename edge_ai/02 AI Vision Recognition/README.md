# 01 AI Vision Recognition

Point the camera at everyday objects — the AI detects and labels them in real time. This project uses the `VideoObjectDetection` brick with a general object detection model that can recognize cups, people, cell phones, and many other common items.

![Result](assets/docs_assets/vision_result.png)

## Hardware Requirements

### Hardware

- Arduino UNO Q ×1
- Multimedia Carrier with CSI camera
- USB-C cable ×1

### Software

- Arduino App Lab

## Prerequisites

1. Open App Lab settings.
2. Enable the external carrier.
3. Configure the camera port as `type1-2lanes`.
4. Reboot the board.

## Wiring

The IMU is built into the Multimedia Carrier — no breadboard wiring needed. Just attach the carrier to the UNO Q.

![Wiring](assets/docs_assets/wiring_camera.png)

## How to Use

1. Import `01 AI Vision Recognition.zip` into **Arduino App Lab**.
2. Click **Run**.
3. Open the Web UI — the camera feed appears on the left, detected objects on the right.
4. Show a cup, person, or cell phone to the camera — the detection panel updates in real time.

## How it Works

```text
CSI Camera → VideoObjectDetection brick (general model)
    │
    ├── Video stream → port 4912/embed → <iframe> in Web UI
    │
    └── Detections → socket.io → detection panel in Web UI
```

The general object detection model recognizes ~80 common object categories. Each detection includes a **confidence score** (0–100%) — higher means more certain. The `debounce_sec` setting prevents the same object from triggering rapid repeated callbacks.
