# 03 Voice Recorder

The **Voice Recorder** example turns the UNO Q into a dictaphone: press one button to record your voice, press it again to stop and save, then press the other button to play the recording back through the speaker.

## Software

### Bricks Used

This example uses the following Bricks:

- `sunfounder_stt` — Microphone recording (recording API only, no speech recognition in this lesson)
- `sunfounder_tts` — Speaker playback (plays the saved audio file, no text synthesis in this lesson)

## Hardware

- Pan Tilt Kit ×1
- Push button ×2
- Breadboard ×1
- Jumper wires
- USB-C cable ×1

## Wiring

Connect the two push buttons between D7 / D6 and GND:

- Record button: pin 1 → **D7**, pin 2 → **GND**
- Play button: pin 1 → **D6**, pin 2 → **GND**

![Wiring Diagram](assets/docs_assets/wiring_two_buttons.png)

No external resistors are needed — the sketch uses the internal pull-up resistors. The microphone and speaker are built into the Multimedia Carrier.

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `03 Voice Recorder.zip` from `unoq-ai-kit\media`.
4. Click **Run**.
5. Wait for `Ready.` in the **Output** window, then:
   - Press the **D7 button** once — **Recording...** appears; speak into the microphone.
   - Press **D7** again — **Recording saved.** appears.
   - Press the **D6 button** once — **Playing...** appears and the speaker plays your recording.
   - Press **D6** again to stop playback.

> **Note:** The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

## How it Works

- D7 pressed → `record_button_read` returns 1 → `stt.start_recording()`
- D7 pressed again → `stt.stop_recording(AUDIO_FILE)` → recording saved to `stt_last.wav`
- D6 pressed → `tts.play_audio(AUDIO_FILE)` → speaker plays the file
- D6 pressed again → `tts.stop_audio()` → playback stops

- The STT Brick is used only for **microphone recording** here — no speech recognition runs. The audio is saved to a WAV file instead of being transcribed.
- The TTS Brick is used only for **speaker playback** — it plays the saved WAV file, it does not synthesize any text.
- Python compares each button reading with the previous one, so each press toggles exactly one action — the same edge-detection pattern used in the other button lessons.
- Recording and playback never run at the same time: starting a recording stops any playback first, and the play button is ignored while recording.
