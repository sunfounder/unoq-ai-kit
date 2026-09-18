# 05 IoT Voice Announcer

Type a message in the Web UI and let the UNO Q speak it aloud through the speaker.

## Software

### Bricks Used

- `web_ui` — Creates the web interface and provides real-time communication between the browser and the Python backend
- `sunfounder_tts` — Converts the typed text to speech and plays it through the speaker

## Hardware

- Pan Tilt Kit ×1
- USB-C cable ×1

## Wiring

No breadboard wiring is needed — the speaker is built into the Multimedia Carrier.

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Download [05 IoT Voice Announcer.zip](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/05.IoT.Voice.Announcer.zip) and import it in **Arduino App Lab**.
4. Click **Run**.
5. In the Web UI, type a short message and click **Speak** — the status changes to **Speaking...**, the UNO Q reads your message aloud, and then the status returns to **Ready to speak another message.**

## How it Works

- Type a message and click **Speak** → the browser sends a `speak_message` event to Python
- Python checks the text, sends a **Speaking...** status to the Web UI, and calls `tts.say(text)`
- When playback finishes, Python sends **Ready to speak another message.** back to the Web UI
- Empty messages are rejected with **Please enter a message.**, and long messages are trimmed to 300 characters so one click never triggers a huge announcement

- The example uses `EdgeTTS`, so the UNO Q needs Internet access for speech generation.
