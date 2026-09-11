# 07 Voice-Controlled Pan-Tilt

The **Voice-Controlled Pan-Tilt** example uses local speech recognition to control a two-servo pan-tilt: hold the button, say a command such as "Turn left", release the button, and the pan-tilt moves while the speaker confirms the action — speech → hardware → spoken feedback.

## Software

### Bricks Used

This example uses the following Bricks:

- `sunfounder_stt` — Local speech-to-text engine (Whisper model)
- `sunfounder_tts` — Local text-to-speech engine (EdgeTTS)

### Libraries Used

- **Arduino_HardwareServo** library

## Hardware

- Pan Tilt Kit ×1
- Push button ×1
- Breadboard ×1
- Jumper wires
- USB-C cable ×1

## Wiring

Connect the servos to the Robot Shield and the push button to the UNO Q:

- Pan servo → **D9**
- Tilt servo → **D10**
- Button pin 1 → **D4**
- Button pin 2 → **GND**

![Wiring Diagram](assets/docs_assets/wiring_pan_tilt_button.png)

No external resistor is needed for the button — the sketch uses the internal pull-up resistor.

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `07 Voice-Controlled Pan-Tilt.zip` from `unoq-ai-kit\media`.
4. Click **Run**.
5. Wait for `Voice-controlled pan-tilt is ready.` in the **Output** window, then hold the button and say a command (for example, "Turn left"), and release the button — the pan-tilt moves to the matching angle and the speaker confirms: *"Turning left."*

Supported commands: `Turn left`, `Turn right`, `Look up`, `Look down`, and `Center` (short forms such as `left`, `right`, `up`, `down` also work).

> **Note:** The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

## How it Works

- Button pressed → starts recording
- Button released → stops recording and recognizes
- `match_command(text)` → "turn left" → ("pan_left", "Turning left.", "Turning left.")
- `Bridge.call("pan_left", "")` → the pan servo moves to 135°
- `tts.say("Turning left.")` → spoken feedback

- The `COMMANDS` table maps voice phrases to three things: the Bridge RPC to call, the spoken feedback, and the console message.
- `match_command()` normalizes the text (lowercase, single spaces) and checks every phrase in the table, so full sentences and short forms both match.
- Speech → action → speech feedback: the robot confirms what it did instead of simply repeating the command.
