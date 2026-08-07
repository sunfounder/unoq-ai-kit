# 01 Local TTS

The **Local TTS** example makes the UNO Q speak aloud — "Hello! Welcome to Arduino App Lab." It introduces the `EdgeTTS` engine, which converts text into speech and plays it through the Multimedia Carrier's speaker. No button, no web page, no wiring — just a few lines of Python.

## Software

### Bricks Used

This example uses the following Bricks:

- `robot_shield` — Provides access to the Robot Shield hardware (I2C, GPIO, audio, PWM)
- `sunfounder_tts` — Local text-to-speech engine (EdgeTTS)

### Libraries Used

- **RobotShield** library (install via Library Manager)
- **SunFounder_TTS** library (install via Library Manager)

## Hardware

- Arduino UNO Q ×1
- Multimedia Carrier
- USB-C cable ×1

## Wiring

No breadboard wiring is needed. The speaker is built into the Multimedia Carrier — just attach the carrier to the UNO Q.

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **My Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `01 Local TTS.zip` from `unoq-ai-kit\media`.
4. Click **Run**.
5. The speaker on the Multimedia Carrier says: *"Hello! Welcome to Arduino App Lab."*

## How it Works

```text
EdgeTTS(gain=0.4)      → create the TTS engine
tts.set_voice(...)      → choose a voice
tts.say("Hello! ...")   → convert text to speech and play
```

- `EdgeTTS` is a text-to-speech engine that runs locally — no API key needed. It downloads voice models on first use.
- `gain=0.4` controls the volume, from 0.0 (silent) to 1.0 (maximum).
- `set_voice("en-US-JennyNeural")` chooses an American English female voice. Other options include `en-US-GuyNeural` (male) and `en-GB-SoniaNeural` (British).

## Code Overview

### Python

`python/main.py` runs on the Linux MPU.

```python
from arduino.app_utils import App
from sunfounder_tts import EdgeTTS

tts = EdgeTTS(gain=0.4)
tts.set_voice("en-US-JennyNeural")

print("Speaking...")
tts.say("Hello! Welcome to Arduino App Lab.")
print("Done.")

def loop():
    time.sleep(10)

App.run(user_loop=loop)
```

- `EdgeTTS(gain=0.4)` — Creates the TTS engine with 40% volume.
- `tts.set_voice(...)` — Selects the voice character. Change this string to use a different voice.
- `tts.say(text)` — Converts the text to speech and plays it through the speaker. Blocks until finished.
- `App.run(user_loop=loop)` — Keeps the Python app alive after the speech finishes.
