# 06 STT Echo

The **STT Echo** example closes the speech loop: hold the button, say a sentence, release the button, and the UNO Q recognizes your speech locally and repeats it aloud through the speaker — speech to text, then text back to speech.

## Software

### Bricks Used

This example uses the following Bricks:

- `sunfounder_stt` — Local speech-to-text engine (Whisper model)
- `sunfounder_tts` — Local text-to-speech engine (EdgeTTS)

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

No external resistor is needed — the sketch uses the Arduino internal pull-up resistor. The speaker is built into the Multimedia Carrier.

## How to Use the Example

1. Download [`06 STT Echo.zip`](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/06.STT.Echo.zip).
2. In App Lab, go to **Apps** → **Create New App** → **Import App** → **Import from Computer** and open the package you downloaded.
3. Click **Run**.
4. Wait for `STT Echo is ready.` in the **Output** window, then hold the button and speak. When you release the button, the recognized sentence appears after `You said:` and the speaker repeats it aloud.

> **Note:** The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

## How it Works

- Button pressed → starts recording
- Button released → stops recording
- `text = stt.get_result()` → "Hello Arduino"
- `print(f"You said: {text}")` → shows the result in the Output window
- `tts.say(text)` → the speaker repeats it aloud

- STT turns your speech into text, and TTS turns that text back into speech — the same text is both printed and spoken.
- The microphone is not recording while the speaker plays, so the reply is never picked up and re-recognized.
