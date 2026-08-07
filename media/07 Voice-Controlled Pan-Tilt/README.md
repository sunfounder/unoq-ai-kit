# 07 Voice-Controlled Pan-Tilt

The **Voice-Controlled Pan-Tilt** example uses local speech recognition to control a two-servo pan-tilt: hold the button, say a command such as "Turn left", release the button, and the pan-tilt moves while the speaker confirms the action — speech → hardware → spoken feedback.

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
- Push button ×1
- Breadboard ×1
- Jumper wires
- USB-C cable ×1

## Wiring

Connect the servos to the Robot Shield and the push button to the UNO Q:

- Pan servo → **P0**
- Tilt servo → **P1**
- Button pin 1 → **D2**
- Button pin 2 → **GND**

![Wiring Diagram](assets/docs_assets/wiring_pan_tilt_button.png)

No external resistor is needed for the button — the sketch uses the internal pull-up resistor.

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **My Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `07 Voice-Controlled Pan-Tilt.zip` from `unoq-ai-kit\media`.
4. Click **Run**.
5. Wait for `Voice-controlled pan-tilt is ready.` in the **Output** window, then hold the button and say a command (for example, "Turn left"), and release the button — the pan-tilt moves to the matching angle and the speaker confirms: *"Turning left."*

Supported commands: `Turn left`, `Turn right`, `Look up`, `Look down`, and `Center` (short forms such as `left`, `right`, `up`, `down` also work).

## How it Works

```text
Button pressed → start recording
    ↓
Button released → stop recording and recognize
    ↓
match_command(text) → "turn left" → ("pan_left", "Turning left.", "Pan: -45°")
    ↓
Bridge.call("pan_left", "") → pan servo moves to -45°
    ↓
tts.say("Turning left.") → spoken feedback
```

- The `COMMANDS` table maps voice phrases to three things: the Bridge RPC to call, the spoken feedback, and the console message.
- `match_command()` normalizes the text (lowercase, single spaces) and checks every phrase in the table, so full sentences and short forms both match.
- Speech → action → speech feedback: the robot confirms what it did instead of simply repeating the command.

## Code Overview

### Python

`python/main.py` runs on the Linux MPU.

```python
import time
from typing import Optional, Tuple

from arduino.app_utils import Bridge

from sunfounder_stt import STT
from sunfounder_tts import EdgeTTS

BUTTON_RPC = "button_read"
POLL_INTERVAL = 0.05
MIN_RECORDING_TIME = 0.5

# Each entry is: phrases, Bridge RPC, spoken feedback, console action.
COMMANDS = (
    (("turn left", "look left", "left"), "pan_left", "Turning left.", "Pan: -45°"),
    (("turn right", "look right", "right"), "pan_right", "Turning right.", "Pan: 45°"),
    (("look up", "turn up", "up"), "tilt_up", "Looking up.", "Tilt: -45°"),
    (("look down", "turn down", "down"), "tilt_down", "Looking down.", "Tilt: 45°"),
    (("center", "centre", "look forward", "return to center"), "center", "Returning to center.", "Pan: 0°, Tilt: 0°"),
)


def match_command(text: str) -> Optional[Tuple[str, str, str]]:
    """Return the RPC, feedback, and console action for recognized text."""
    normalized = " ".join(text.lower().strip().split())

    for phrases, rpc_name, feedback, action in COMMANDS:
        if any(phrase in normalized for phrase in phrases):
            return rpc_name, feedback, action

    return None


print("Preparing the audio input and output...", flush=True)

stt = STT(type="local_fast", language="en")
tts = EdgeTTS(gain=0.4)
tts.set_voice("en-US-JennyNeural")

print("Voice-controlled pan-tilt is ready.", flush=True)
print("Supported commands:", flush=True)
print("  Turn left | Turn right | Look up | Look down | Center", flush=True)
print("Hold the button and speak. Release it to recognize.", flush=True)

last_state = 0
recording = False
recording_started_at = 0.0

while True:
    state = int(Bridge.call(BUTTON_RPC, ""))

    # Button pressed: start recording.
    if state == 1 and last_state == 0 and not recording:
        print("\nListening...", flush=True)
        stt.start_listening()
        recording = True
        recording_started_at = time.monotonic()

    # Button released: stop recording and recognize the command.
    elif state == 0 and last_state == 1 and recording:
        recording_time = time.monotonic() - recording_started_at

        if recording_time < MIN_RECORDING_TIME:
            time.sleep(MIN_RECORDING_TIME - recording_time)

        print("Recognizing...", flush=True)
        stt.stop_listening()
        text = stt.get_result()
        recording = False

        if text and text.strip():
            recognized_text = text.strip()
            print("Recognized:", flush=True)
            print(recognized_text, flush=True)

            command = match_command(recognized_text)

            if command is None:
                print("Command not recognized.", flush=True)
                tts.say("Command not recognized.")
            else:
                rpc_name, feedback, action = command
                Bridge.call(rpc_name, "")
                print(action, flush=True)
                tts.say(feedback)
        else:
            print("No speech recognized.", flush=True)

    last_state = state
    time.sleep(POLL_INTERVAL)
```

- `COMMANDS` — A table of (phrases, Bridge RPC, spoken feedback, console action) entries.
- `match_command(text)` — Finds the first entry whose phrase appears in the recognized text; returns `None` when nothing matches.
- `Bridge.call(rpc_name, "")` — Calls the matched servo function on the sketch.
- `tts.say(feedback)` — Speaks the confirmation, for example "Turning left."

### Sketch

`sketch/sketch.ino` runs on the STM32 MCU.

```cpp
#include <Arduino_RouterBridge.h>
#include "RobotShield.h"

const int BUTTON_PIN = 2;

const int LEFT_ANGLE = -45;
const int RIGHT_ANGLE = 45;
const int UP_ANGLE = -45;
const int DOWN_ANGLE = 45;
const int CENTER_ANGLE = 0;

Servo panServo(0);
Servo tiltServo(1);

int buttonRead(String dummy)
{
    (void)dummy;
    return digitalRead(BUTTON_PIN) == LOW ? 1 : 0;
}

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
    pinMode(BUTTON_PIN, INPUT_PULLUP);

    I2cBus::i2c().begin();
    panServo.begin();
    tiltServo.begin();

    panServo.setAngle(CENTER_ANGLE);
    tiltServo.setAngle(CENTER_ANGLE);

    Bridge.begin();
    Bridge.provide("button_read", buttonRead);
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
- `Bridge.provide(...)` — Registers all five servo functions plus `button_read` so Python can call them.
