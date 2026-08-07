# 08 Camera Snapshot

The **Camera Snapshot** example captures a photo with the camera whenever you press the button: one press, one JPEG image saved in the `photos` folder with automatic numbering.

## Software

### Bricks Used

This example uses the following Bricks:

- `robot_shield` — Provides access to the Robot Shield hardware (I2C, GPIO, audio, PWM)

### Libraries Used

- **RobotShield** library (install via Library Manager)

## Hardware

- Arduino UNO Q ×1
- Multimedia Carrier ×1
- Push button ×1
- Breadboard ×1
- Jumper wires
- USB-C cable ×1

## Wiring

Connect the push button between **D2** and **GND**:

- Button pin 1 → **D2**
- Button pin 2 → **GND**

![Wiring Diagram](assets/docs_assets/wiring_button.png)

No external resistor is needed — the sketch uses the Arduino internal pull-up resistor. The camera is built into the Multimedia Carrier.

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **My Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `08 Camera Snapshot.zip` from `unoq-ai-kit\media`.
4. Click **Run**.
5. Wait for `Camera ready.` in the **Output** window, then press the button — a photo is captured and saved as `photos/photo_001.jpg` (the next press saves `photo_002.jpg`, and so on).

## How it Works

```text
Button pressed → Bridge.call("button_read") returns 1
    ↓
camera.capture() → grab one frame
    ↓
cv2.flip(frame, 0) → correct the vertical orientation
    ↓
next_photo_path() → "photos/photo_001.jpg"
    ↓
cv2.imwrite(...) → save the photo
```

- The camera is an App Lab peripheral (`arduino.app_peripherals.camera`) and is started with `camera.start()`.
- Photos are saved as JPEG files in the `photos` folder and numbered automatically.
- `next_photo_path()` scans for the first unused number, so restarting the app never overwrites previous photos.

## Code Overview

### Python

`python/main.py` runs on the Linux MPU.

```python
import time
from pathlib import Path

import cv2

from arduino.app_peripherals.camera import Camera
from arduino.app_utils import Bridge

BUTTON_RPC = "button_read"
POLL_INTERVAL = 0.05
PHOTO_DIR = Path("/app/photos")


def next_photo_path() -> Path:
    """Return the next unused photo filename."""
    index = 1

    while True:
        path = PHOTO_DIR / f"photo_{index:03d}.jpg"

        if not path.exists():
            return path

        index += 1


PHOTO_DIR.mkdir(parents=True, exist_ok=True)

print("Initializing camera...", flush=True)
camera = Camera()
camera.start()
time.sleep(1)

print("Camera ready.", flush=True)
print("Press the button to take a photo.", flush=True)

last_state = 0

while True:
    state = int(Bridge.call(BUTTON_RPC, ""))

    # Capture once when the button changes from released to pressed.
    if state == 1 and last_state == 0:
        print("\nCapturing...", flush=True)

        frame = camera.capture()

        # Flip the image vertically.
        frame = cv2.flip(frame, 0)

        photo_path = next_photo_path()

        if cv2.imwrite(str(photo_path), frame):
            print(
                f"Photo saved: photos/{photo_path.name}",
                flush=True,
            )
        else:
            print("Failed to save photo.", flush=True)

    last_state = state
    time.sleep(POLL_INTERVAL)
```

- `Camera()` / `camera.start()` — Initializes and starts the camera.
- `camera.capture()` — Grabs a single frame from the camera.
- `cv2.flip(frame, 0)` — Flips the image vertically to correct its orientation.
- `next_photo_path()` — Returns the next unused `photo_NNN.jpg` filename.
- `cv2.imwrite(...)` — Saves the frame as a JPEG file.

### Sketch

`sketch/sketch.ino` runs on the STM32 MCU.

```cpp
#include <Arduino_RouterBridge.h>

const int BUTTON_PIN = 2;

int buttonRead(String dummy)
{
    (void)dummy;
    return digitalRead(BUTTON_PIN) == LOW ? 1 : 0;
}

void setup()
{
    pinMode(BUTTON_PIN, INPUT_PULLUP);

    Bridge.begin();
    Bridge.provide("button_read", buttonRead);
}

void loop()
{
    delay(10);
}
```

- `pinMode(BUTTON_PIN, INPUT_PULLUP)` — Enables the internal pull-up resistor, so no external resistor is needed.
- `digitalRead(BUTTON_PIN) == LOW ? 1 : 0` — Pressing the button connects D2 to GND; the function returns `1` while pressed.
- `Bridge.provide("button_read", buttonRead)` — Registers the function so Python can call it via Bridge.
