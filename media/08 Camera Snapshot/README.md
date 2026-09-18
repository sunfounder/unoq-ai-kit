# 08 Camera Snapshot

The **Camera Snapshot** example captures a photo with the camera whenever you press the button: one press, one JPEG image saved in the `photos` folder with automatic numbering.

## Hardware

- Pan Tilt Kit ×1
- Push button ×1
- Breadboard ×1
- Jumper wires
- USB-C cable ×1

## Wiring

Connect the push button between **D4** and **GND**:

- Button pin 1 → **D4**
- Button pin 2 → **GND**

![Wiring Diagram](assets/docs_assets/wiring_button.png)

No external resistor is needed — the sketch uses the Arduino internal pull-up resistor. The camera is built into the Multimedia Carrier.

## How to Use the Example

1. Download [`08 Camera Snapshot.zip`](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/08.Camera.Snapshot.zip).
2. In App Lab, go to **Apps** → **Create New App** → **Import App** → **Import from Computer** and open the package you downloaded.
3. Click **Run**.
4. Wait for `Camera ready.` in the **Output** window, then press the button — a photo is captured and saved as `photos/photo_001.jpg` (the next press saves `photo_002.jpg`, and so on).

## How it Works

- Button pressed → `Bridge.call("button_read")` returns 1
- `camera.capture()` → grabs one frame
- `cv2.flip(frame, 0)` → corrects the vertical orientation
- `next_photo_path()` → "photos/photo_001.jpg"
- `cv2.imwrite(...)` → saves the photo

- The camera is an App Lab peripheral (`arduino.app_peripherals.camera`) and is started with `camera.start()`.
- Photos are saved as JPEG files in the `photos` folder and numbered automatically.
- `next_photo_path()` scans for the first unused number, so restarting the app never overwrites previous photos.
