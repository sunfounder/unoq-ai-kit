# 01 Local TTS

The **Local TTS** example makes the UNO Q speak aloud — "Hello! Welcome to Arduino App Lab." It introduces the `EdgeTTS` engine, which converts text into speech and plays it through the Multimedia Carrier's speaker. No button, no web page, no wiring — just a few lines of Python.

## Software

### Bricks Used

This example uses the following Bricks:

- `sunfounder_tts` — Local text-to-speech engine (EdgeTTS)

## Hardware

- Pan Tilt Kit ×1
- USB-C cable ×1

## Wiring

No breadboard wiring is needed. The speaker is built into the Multimedia Carrier — just attach the carrier to the UNO Q.

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `01 Local TTS.zip` from `unoq-ai-kit\media`.
4. Click **Run**.
5. The speaker on the Multimedia Carrier says: *"Hello! Welcome to Arduino App Lab."*

> **Note:** The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

## How it Works

- `EdgeTTS()` → creates the TTS engine
- `tts.set_voice(...)` → chooses a voice
- `tts.set_volume(50)` → sets the speaker volume (default 50)
- `tts.say("Hello! ...")` → converts text to speech and plays

- `EdgeTTS` is a text-to-speech engine that runs locally — no API key needed. It downloads voice models on first use.

- `set_voice("en-US-JennyNeural")` chooses an American English female voice. Other options include `en-US-GuyNeural` (male) and `en-GB-SoniaNeural` (British).
