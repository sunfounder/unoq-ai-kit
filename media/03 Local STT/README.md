# 03 Local STT

The **Local STT** example makes the UNO Q listen with its microphone, transcribe your speech locally with the Whisper model, and print the recognized text in the App Lab **Output** window — no button, no web page, no internet connection needed.

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
- USB-C cable ×1

## Wiring

No breadboard wiring is needed. The microphone is built into the Multimedia Carrier — just attach the carrier to the UNO Q.

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **My Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `03 Local STT.zip` from `unoq-ai-kit\media`.
4. Click **Run**.
5. Wait for `Local STT is ready.` in the **Output** window, then speak toward the UNO Q. After about 5 seconds the recognized sentence appears after `You said:`, and the program listens again automatically. The first run takes longer while the Whisper model is downloaded.

## How it Works

```text
STT(type="local_fast")  → load the local Whisper model
stt.start_listening()   → start recording
time.sleep(5)           → record for 5 seconds
stt.stop_listening()    → stop recording
stt.get_result()        → transcribe the speech locally
print("You said: ...")  → show the result in the Output window
```

- Speech recognition runs entirely on the UNO Q — no internet connection or API key is needed.
- The STT loop runs in a background thread while `App.run()` keeps the app alive.
- An empty result is printed as "No speech detected." — for example, when the microphone hears only silence.

## Code Overview

### Python

`python/main.py` runs on the Linux MPU.

```python
import threading
import time

from arduino.app_utils import App
from sunfounder_stt import STT

# Recording duration for each listening cycle, in seconds.
LISTEN_SECONDS = 5


def stt_worker():
    """Continuously record short clips and transcribe them locally."""
    try:
        print("Preparing the audio input...", flush=True)
        print("Loading the local STT model...", flush=True)
        stt = STT(type="local_fast", language="en")

        print("Local STT is ready.", flush=True)
        print(f"The microphone will listen for {LISTEN_SECONDS} seconds each time.", flush=True)

        while True:
            try:
                stt.reset()

                print("\nListening... Please speak.", flush=True)
                stt.start_listening()
                time.sleep(LISTEN_SECONDS)
                stt.stop_listening()

                print("Recognizing locally...", flush=True)
                text = stt.get_result(timeout=60)
                text = text.strip() if text else ""

                if text:
                    print(f"You said: {text}", flush=True)
                else:
                    print("No speech detected.", flush=True)

                time.sleep(1)

            except Exception as error:
                print(f"STT cycle error: {error}", flush=True)
                try:
                    stt.stop_listening()
                except Exception:
                    pass
                time.sleep(2)

    except Exception as error:
        print(f"Local STT initialization failed: {error}", flush=True)


threading.Thread(target=stt_worker, daemon=True).start()

print("Local STT demo started.", flush=True)
App.run()
```

- `STT(type="local_fast", language="en")` — Creates the local speech-recognition engine with the Whisper model. The model is downloaded on the first run.
- `stt.start_listening()` / `stt.stop_listening()` — Start and stop recording from the microphone.
- `stt.get_result(timeout=60)` — Transcribes the recording locally and returns the recognized text.
- `threading.Thread(...)` — Runs the STT loop in a background thread so the app stays responsive.
- `App.run()` — Keeps the app alive after the background thread has started.
