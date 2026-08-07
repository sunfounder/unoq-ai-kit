# 06 STT Echo

The **STT Echo** example closes the speech loop: hold the button, say a sentence, release the button, and the UNO Q recognizes your speech locally and repeats it aloud through the speaker — speech to text, then text back to speech.

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
- Push button ×1
- Breadboard ×1
- Jumper wires
- USB-C cable ×1

## Wiring

Connect the push button between **D2** and **GND**:

- Button pin 1 → **D2**
- Button pin 2 → **GND**

![Wiring Diagram](assets/docs_assets/wiring_button.png)

No external resistor is needed — the sketch uses the Arduino internal pull-up resistor. The speaker is built into the Multimedia Carrier.

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **My Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `06 STT Echo.zip` from `unoq-ai-kit\media`.
4. Click **Run**.
5. Wait for `STT Echo is ready.` in the **Output** window, then hold the button and speak. When you release the button, the recognized sentence appears after `You said:` and the speaker repeats it aloud.

## How it Works

```text
Button pressed → start recording
    ↓
Button released → stop recording
    ↓
text = stt.get_result() → "Hello Arduino"
    ↓
print(f"You said: {text}") → show in the Output window
    ↓
tts.say(text) → speaker repeats it aloud
```

- STT turns your speech into text, and TTS turns that text back into speech — the same text is both printed and spoken.
- The microphone is not recording while the speaker plays, so the reply is never picked up and re-recognized.

## Code Overview

### Python

`python/main.py` runs on the Linux MPU.

```python
import time

from arduino.app_utils import Bridge

from sunfounder_stt import STT
from sunfounder_tts import EdgeTTS

BUTTON_RPC = "button_read"
POLL_INTERVAL = 0.05
MIN_RECORDING_TIME = 0.5

tts = EdgeTTS(gain=0.4)
tts.set_voice("en-US-JennyNeural")

print("Preparing the audio input...", flush=True)
stt = STT(type="local_fast", language="en")

print("STT Echo is ready.", flush=True)
print("Hold the button and speak. Release it to recognize and repeat.", flush=True)

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

    # Button released: stop recording, recognize, and speak.
    elif state == 0 and last_state == 1 and recording:
        recording_time = time.monotonic() - recording_started_at

        if recording_time < MIN_RECORDING_TIME:
            time.sleep(MIN_RECORDING_TIME - recording_time)

        print("Recognizing...", flush=True)
        stt.stop_listening()
        text = stt.get_result()

        if text and text.strip():
            text = text.strip()
            print(f"You said: {text}")
            tts.say(text)
        else:
            print("No speech detected.", flush=True)

        recording = False

    last_state = state
    time.sleep(POLL_INTERVAL)
```

- `EdgeTTS(gain=0.4)` — Creates the text-to-speech engine at 40% volume.
- `tts.set_voice("en-US-JennyNeural")` — Selects an American English female voice.
- `stt.get_result()` — Returns the recognized sentence.
- `tts.say(text)` — Speaks the recognized sentence through the speaker.

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
