# 04 Local STT

In the previous lesson, the UNO Q recorded your voice and played it back — but it didn't understand a word. Now the board will **transcribe** your speech: it listens with its microphone, turns your words into text locally with the Whisper model, and prints the recognized sentence in the App Lab **Output** window — no button, no web page, no internet connection needed.

## Software

### Bricks Used

This example uses the following Bricks:

- `sunfounder_stt` — Local speech-to-text engine (Whisper model)

## Hardware

- Pan Tilt Kit ×1
- USB-C cable ×1

## Wiring

No breadboard wiring is needed. The microphone is built into the Multimedia Carrier — just attach the carrier to the UNO Q.

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `04 Local STT.zip` from `unoq-ai-kit\media`.
4. Click **Run**.
5. Wait for `Local STT is ready.` in the **Output** window, then speak toward the UNO Q. After about 5 seconds the recognized sentence appears after `You said:`, and the program listens again automatically. The first run takes longer while the Whisper model is loaded.

## How it Works

- `STT(type="local_fast")` → loads the local Whisper model
- `stt.start_listening()` → starts recording
- `time.sleep(5)` → records for 5 seconds
- `stt.stop_listening()` → stops recording
- `stt.get_result()` → transcribes the speech locally
- `print("You said: ...")` → shows the result in the Output window

- Speech recognition runs entirely on the UNO Q — no internet connection or API key is needed.
- The STT loop runs in a background thread while `App.run()` keeps the app alive.
- An empty result is printed as "No speech detected." — for example, when the microphone hears only silence.
