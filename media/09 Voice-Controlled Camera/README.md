# 09 Voice-Controlled Camera

The **Voice-Controlled Camera** example combines everything: speak a command like "Take photo" or "Turn left", and the UNO Q recognizes it locally, moves the pan-tilt or captures a photo, then confirms the action aloud — speech → command → action → feedback, hands-free.

## Software

### Bricks Used

This example uses the following Bricks:

- `sunfounder_stt` — Local speech-to-text engine (Whisper model)
- `sunfounder_tts` — Local text-to-speech engine (EdgeTTS)

### Libraries Used

- **Arduino_HardwareServo** library

## Hardware

- Pan Tilt Kit ×1
- USB-C cable ×1

## Wiring

Connect the servos to the Robot Shield:

- Pan servo → **D9**
- Tilt servo → **D10**

![Wiring Diagram](assets/docs_assets/wiring_pan_tilt.png)

No push button is used — the microphone on the Multimedia Carrier listens automatically. The camera is built into the Multimedia Carrier too.

## How to Use the Example

1. Download [`09 Voice-Controlled Camera.zip`](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/09.Voice-Controlled.Camera.zip).
2. In App Lab, go to **Apps** → **Create New App** → **Import App** → **Import from Computer** and open the package you downloaded.
3. Click **Run**.
4. Wait for `Voice-controlled camera is ready.` in the **Output** window, then speak a command into the microphone — say "Take photo" and a photo is saved as `photos/photo_001.jpg`, or say "Turn left" and the pan-tilt moves. The speaker confirms each action, then the microphone listens again automatically.

Supported commands: `Turn left`, `Turn right`, `Look up`, `Look down`, `Center`, and `Take photo` (short forms such as `left`, `right`, `up`, `down` also work).

> **Note:** The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

## How it Works

- `stt.start_listening()` → listens for 4 seconds
- `stt.get_result()` → "Take photo"
- `match_command(text)` → `take_photo()`
- `action()` → moves a servo or captures a photo
- `tts.say(feedback)` → spoken confirmation, then listens again

- No button: the microphone listens automatically in 4-second cycles and restarts after each action.
- Each voice phrase maps to an action function (`move_left()`, `move_right()`, `move_up()`, `move_down()`, `move_center()`, `take_photo()`).
- TTS feedback only runs after listening has stopped, so the speaker's own voice is never picked up as a new command.
