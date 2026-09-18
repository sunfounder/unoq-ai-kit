# 10 IoT Voice Message

Record a real voice message with the UNO Q microphone, watch the live audio level in the Web UI, then play the recording through the speaker.

## Software

### Bricks Used

- `web_ui` — Creates the web interface and provides real-time communication between the browser and the Python backend
- `sunfounder_stt` — Microphone input (recording API only, no speech recognition in this lesson)
- `sunfounder_tts` — Speaker output (plays the recorded WAV file, no text synthesis in this lesson)

## Hardware

- Pan Tilt Kit ×1
- USB-C cable ×1

## Wiring

No breadboard wiring is needed — the microphone and speaker are built into the Multimedia Carrier.

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Download [10 IoT Voice Message.zip](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/10.IoT.Voice.Message.zip) and import it in **Arduino App Lab**.
4. Click **Run**.
5. In the Web UI: click **Record** and speak into the microphone while watching the live audio level, click **Stop** to save the recording, then click **Play** to hear it through the speaker. **Pause** pauses playback, and **Play** resumes it.

## How it Works

- **Record** → `stt.start_recording()` opens the microphone; the audio level is streamed to the Web UI in real time
- **Stop** → `stt.stop_recording(AUDIO_FILE)` saves the clip as a WAV file
- **Play** → `tts.play_audio(AUDIO_FILE)` sends the saved clip to the speaker
- **Pause / Play** → pause and resume the playback

- The speaker volume is set with `tts.set_volume(50)` — change the value for louder or quieter playback.
- No speech recognition runs in this lesson, so no local Whisper model is included.
