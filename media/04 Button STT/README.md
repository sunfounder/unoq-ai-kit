# 04 Button STT

The **Button STT** example adds a push button to local speech recognition: hold the button to start recording, release it to stop, and the UNO Q transcribes your speech locally and prints the result in the App Lab **Output** window.

## Software

### Bricks Used

This example uses the following Bricks:

- `robot_shield` — Provides access to the Robot Shield hardware (I2C, GPIO, audio, PWM)
- `sunfounder_stt` — Local speech-to-text engine (Whisper model)

### Libraries Used

- **RobotShield** library (install via Library Manager)
- **SunFounder_STT** library (install via Library Manager)

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

No external resistor is needed — the sketch uses the Arduino internal pull-up resistor.

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **My Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `04 Button STT.zip` from `unoq-ai-kit\media`.
4. Click **Run**.
5. Wait for `Local STT is ready.` in the **Output** window, then hold the button and speak. When you release the button, the recognized sentence appears after `You said:`.

## How it Works

```text
Button pressed  → sketch returns 1 through button_read
    ↓
stt.start_listening()  → start recording
    ↓
Button released  → sketch returns 0
    ↓
stt.stop_listening()  → stt.get_result() → local transcription
    ↓
print("You said: ...")  → show the recognized text
```

- The sketch reads the button with `INPUT_PULLUP` and reports its state through the Bridge function `button_read` — Python never touches the pin directly.
- Recording starts when the button is pressed and stops when it is released, so you control exactly how long the microphone listens.
- Speech recognition runs entirely on the UNO Q (Whisper model) — no internet connection or API key is needed.

## Code Overview

### Python

`python/main.py` runs on the Linux MPU.

```python
import time

from arduino.app_utils import Bridge
from sunfounder_stt import STT

BUTTON_RPC = "button_read"
POLL_INTERVAL = 0.05
MIN_RECORDING_TIME = 0.5

print("Preparing the audio input...", flush=True)
stt = STT(type="local_fast", language="en")

print("Local STT is ready.", flush=True)
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

    # Button released: stop recording and recognize the speech.
    elif state == 0 and last_state == 1 and recording:
        recording_time = time.monotonic() - recording_started_at

        if recording_time < MIN_RECORDING_TIME:
            time.sleep(MIN_RECORDING_TIME - recording_time)

        print("Recognizing...", flush=True)
        stt.stop_listening()
        text = stt.get_result()

        if text and text.strip():
            print(f"You said: {text.strip()}", flush=True)

        recording = False

    last_state = state
    time.sleep(POLL_INTERVAL)
```

- `Bridge.call("button_read", "")` — Asks the sketch whether the button is pressed; returns `1` while pressed and `0` while released.
- `stt.start_listening()` / `stt.stop_listening()` — Start recording when the button is pressed and stop when it is released.
- `stt.get_result()` — Transcribes the recording locally and returns the recognized text.
- `MIN_RECORDING_TIME` — Presses shorter than 0.5 seconds are treated as accidental taps and are waited out before recognizing.

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
