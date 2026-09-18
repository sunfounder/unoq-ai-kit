# 05 AI Object Counter

Use the AI camera to detect and count three everyday objects: mice, keyboards, and cell phones. Each new appearance increases the matching counter by one, and text-to-speech announces the object name.

![Result](assets/docs_assets/ai_object_counter.png)

## Software

### Bricks Used

This example uses the following Bricks:

- `video_object_detection` — Runs the general object-detection model on every camera frame; Python keeps only the three target classes and ignores everything else
- `web_ui` — Creates the web interface with the live counters and the **RESET COUNTS** button
- `sunfounder_tts` — Synthesizes the spoken object names and plays them through the Multimedia Carrier's speaker (EdgeTTS needs an Internet connection, but no API key)

## Hardware

- Pan Tilt Kit ×1
- USB-C cable ×1

## Wiring

The camera and the speaker are both built into the Multimedia Carrier, so no breadboard wiring is needed.

## How to Use the Example

1. Download [`05 AI Object Counter.zip`](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/05.AI.Object.Counter.zip).
2. In App Lab, go to **Apps** → **Create New App** → **Import App** → **Import from Computer** and open the package you downloaded.
3. Click **Run** and open the Web UI.
4. Show one mouse, keyboard, or cell phone to the camera. Once the model reaches 60% confidence the matching counter goes up by one and the speaker says the object's name. Remove the object completely, then show the next one. Click **RESET COUNTS** to start again.

> **Note:** The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

## Counted Objects

| Class | Counter | Spoken name |
| --- | --- | --- |
| `mouse` | Mouse | "Mouse detected" |
| `keyboard` | Keyboard | "Keyboard detected" |
| `cell phone` | Cell Phone | "Cell phone detected" |

## How it Works

**Flow**

- Brick (`video_object_detection`) — runs the general model on every frame and reports every object it recognizes
- Python (`main.py`) — filters the results down to the three target classes and decides what counts as a new appearance
- Python (`speak()`) — puts the object's name into a speech queue instead of speaking directly in the callback
- Worker thread — takes names off the queue and plays them through `sunfounder_tts` while detection keeps running
- Browser — shows the live counters and the **RESET COUNTS** button

**Counting events, not frames**

The detector processes many frames each second, so adding one on every detection would count the same mouse dozens of times. The program therefore *locks* a class as soon as it has been counted, and only re-arms it after the class has been missing for ten consecutive frames. That is the trick behind any AI counter: the model reports what is in the frame, the program decides what counts as a new event.

**Speaking without stalling the camera**

Speech is slow — synthesizing a phrase takes far longer than one video frame. Instead of calling the TTS engine from the detection callback, `speak()` only puts the text into a queue, and a separate worker thread consumes it. Detection keeps running, so the counters stay responsive while the speaker talks.

**Everything is tunable**

The whole behaviour lives in a few constants at the top of `python/main.py`: `TARGETS` (which classes appear in the Web UI), `CONFIDENCE_THRESHOLD = 0.60` (how sure the model must be before a count is accepted), `MISSING_FRAMES_TO_REARM = 10` (how long an object must be gone before it can be counted again), `TTS_VOICE`, and `TTS_VOLUME`. Change one, click **Run** again, and watch how the counter behaves differently.
