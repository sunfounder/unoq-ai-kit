# 09 Voice-Controlled Camera

The **Voice-Controlled Camera** example combines everything: speak a command like "Take photo" or "Turn left", and the UNO Q recognizes it locally, moves the pan-tilt or captures a photo, then confirms the action aloud — speech → command → action → feedback, hands-free.

## Software

### Bricks Used

This example uses the following Bricks:

- `robot_shield` — Provides access to the Robot Shield hardware (I2C, GPIO, audio, PWM)
- `sunfounder_stt` — Local speech-to-text engine (Whisper model)
- `sunfounder_tts` — Local text-to-speech engine (EdgeTTS)

### Libraries Used

- **RobotShield** library (install via Library Manager)
- **SunFounder_STT** library (install via Library Manager)
- **SunFounder_TTS** library (install via Library Manager)

## Hardware

- Arduino UNO Q ×1
- Robot Shield ×1
- Multimedia Carrier ×1
- Pan-tilt with 2× servos ×1
- USB-C cable ×1

## Wiring

Connect the servos to the Robot Shield:

- Pan servo → **P0**
- Tilt servo → **P1**

![Wiring Diagram](assets/docs_assets/wiring_pan_tilt.png)

No push button is used — the microphone on the Multimedia Carrier listens automatically. The camera is built into the Multimedia Carrier too.

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **My Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `09 Voice-Controlled Camera.zip` from `unoq-ai-kit\media`.
4. Click **Run**.
5. Wait for `Voice-controlled camera is ready.` in the **Output** window, then speak a command into the microphone — say "Take photo" and a photo is saved as `photos/photo_001.jpg`, or say "Turn left" and the pan-tilt moves. The speaker confirms each action, then the microphone listens again automatically.

Supported commands: `Turn left`, `Turn right`, `Look up`, `Look down`, `Center`, and `Take photo` (short forms such as `left`, `right`, `up`, `down` also work).

## How it Works

```text
stt.start_listening() → listen for 4 seconds
    ↓
stt.get_result() → "Take photo"
    ↓
match_command(text) → take_photo()
    ↓
action() → move a servo or capture a photo
    ↓
tts.say(feedback) → spoken confirmation, then listen again
```

- No button: the microphone listens automatically in 4-second cycles and restarts after each action.
- Each voice phrase maps to an action function (`move_left()`, `move_right()`, `move_up()`, `move_down()`, `move_center()`, `take_photo()`).
- TTS feedback only runs after listening has stopped, so the speaker's own voice is never picked up as a new command.

## Code Overview

### Python

`python/main.py` runs on the Linux MPU.

```python
import time
from pathlib import Path
from typing import Callable, Optional

import cv2

from arduino.app_peripherals.camera import Camera
from arduino.app_utils import Bridge

from sunfounder_stt import STT
from sunfounder_tts import EdgeTTS

LISTEN_SECONDS = 4
PAUSE_BETWEEN_CYCLES = 0.8

PHOTO_DIR = Path("/app/photos")
PHOTO_DIR.mkdir(parents=True, exist_ok=True)

print("Preparing audio input and output...", flush=True)

print("Loading local speech recognition...", flush=True)
stt = STT(type="local_fast", language="en")

tts = EdgeTTS(gain=0.4)
tts.set_voice("en-US-JennyNeural")

print("Initializing camera...", flush=True)
camera = Camera()
camera.start()
time.sleep(1)


def next_photo_path() -> Path:
    """Return the next unused photo filename."""
    index = 1

    while True:
        path = PHOTO_DIR / f"photo_{index:03d}.jpg"

        if not path.exists():
            return path

        index += 1


def move_left() -> None:
    Bridge.call("pan_left", "")
    print("Pan: -45°", flush=True)
    tts.say("Turning left.")


def move_right() -> None:
    Bridge.call("pan_right", "")
    print("Pan: 45°", flush=True)
    tts.say("Turning right.")


def move_up() -> None:
    Bridge.call("tilt_up", "")
    print("Tilt: -45°", flush=True)
    tts.say("Looking up.")


def move_down() -> None:
    Bridge.call("tilt_down", "")
    print("Tilt: 45°", flush=True)
    tts.say("Looking down.")


def move_center() -> None:
    Bridge.call("center", "")
    print("Pan: 0°, Tilt: 0°", flush=True)
    tts.say("Returning to center.")


def take_photo() -> None:
    tts.say("Taking a photo.")

    frame = camera.capture()

    # Correct the camera orientation on the pan-tilt mount.
    frame = cv2.flip(frame, 0)

    photo_path = next_photo_path()

    if cv2.imwrite(str(photo_path), frame):
        print(f"Photo saved: photos/{photo_path.name}", flush=True)
        tts.say("Photo saved.")
    else:
        print("Failed to save photo.", flush=True)
        tts.say("Failed to save the photo.")


COMMANDS: tuple[tuple[tuple[str, ...], Callable[[], None]], ...] = (
    (("take a photo", "take photo", "capture a photo", "capture photo"), take_photo),
    (("turn left", "look left", "left"), move_left),
    (("turn right", "look right", "right"), move_right),
    (("look up", "turn up", "up"), move_up),
    (("look down", "turn down", "down"), move_down),
    (("return to center", "look forward", "centre", "center"), move_center),
)


def match_command(text: str) -> Optional[Callable[[], None]]:
    """Return the action that matches the recognized speech."""
    normalized = " ".join(text.lower().strip().split())

    for phrases, action in COMMANDS:
        if any(phrase in normalized for phrase in phrases):
            return action

    return None


print("Voice-controlled camera is ready.", flush=True)
print("Supported commands:", flush=True)
print("  Turn left | Turn right | Look up | Look down | Center | Take photo", flush=True)
print(f"The microphone listens for {LISTEN_SECONDS} seconds each time.", flush=True)

while True:
    try:
        stt.reset()

        print("\nListening... Please speak.", flush=True)
        stt.start_listening()
        time.sleep(LISTEN_SECONDS)
        stt.stop_listening()

        print("Recognizing...", flush=True)
        text = stt.get_result(timeout=60)
        recognized_text = text.strip() if text else ""

        if not recognized_text:
            print("No speech recognized.", flush=True)
        else:
            print(f"Recognized: {recognized_text}", flush=True)
            action = match_command(recognized_text)

            if action is None:
                print("Command not recognized.", flush=True)
                tts.say("Command not recognized.")
            else:
                action()

        # Wait until TTS playback has finished before listening again.
        time.sleep(PAUSE_BETWEEN_CYCLES)

    except Exception as error:
        print(f"Voice-control cycle error: {error}", flush=True)
        time.sleep(2)
```

- `LISTEN_SECONDS` — How long each listening cycle lasts before recognition starts.
- `match_command(text)` — Matches the recognized text to one of the action functions.
- `take_photo()` — Captures a frame, flips it vertically, and saves it as `photos/photo_NNN.jpg`, then speaks "Photo saved."
- `move_left()` / `move_right()` / `move_up()` / `move_down()` / `move_center()` — Call the corresponding servo RPC and speak the confirmation.

### Sketch

`sketch/sketch.ino` runs on the STM32 MCU.

```cpp
#include <Arduino_RouterBridge.h>
#include "RobotShield.h"

const int LEFT_ANGLE = -45;
const int RIGHT_ANGLE = 45;
const int UP_ANGLE = -45;
const int DOWN_ANGLE = 45;
const int CENTER_ANGLE = 0;

Servo panServo(0);
Servo tiltServo(1);

int panLeft(String dummy)
{
    (void)dummy;
    panServo.setAngle(LEFT_ANGLE);
    return LEFT_ANGLE;
}

int panRight(String dummy)
{
    (void)dummy;
    panServo.setAngle(RIGHT_ANGLE);
    return RIGHT_ANGLE;
}

int tiltUp(String dummy)
{
    (void)dummy;
    tiltServo.setAngle(UP_ANGLE);
    return UP_ANGLE;
}

int tiltDown(String dummy)
{
    (void)dummy;
    tiltServo.setAngle(DOWN_ANGLE);
    return DOWN_ANGLE;
}

int centerPanTilt(String dummy)
{
    (void)dummy;
    panServo.setAngle(CENTER_ANGLE);
    tiltServo.setAngle(CENTER_ANGLE);
    return CENTER_ANGLE;
}

void setup()
{
    I2cBus::i2c().begin();

    panServo.begin();
    tiltServo.begin();

    panServo.setAngle(CENTER_ANGLE);
    tiltServo.setAngle(CENTER_ANGLE);

    Bridge.begin();
    Bridge.provide("pan_left", panLeft);
    Bridge.provide("pan_right", panRight);
    Bridge.provide("tilt_up", tiltUp);
    Bridge.provide("tilt_down", tiltDown);
    Bridge.provide("center", centerPanTilt);
}

void loop()
{
    delay(10);
}
```

- `Servo panServo(0)` / `Servo tiltServo(1)` — The pan and tilt servos on ports P0 and P1.
- Each Bridge function (`pan_left`, `pan_right`, ...) moves the matching servo to a fixed angle.
- `centerPanTilt` — Returns both servos to 0°.
- `Bridge.provide(...)` — Registers all five servo functions so Python can call them.
