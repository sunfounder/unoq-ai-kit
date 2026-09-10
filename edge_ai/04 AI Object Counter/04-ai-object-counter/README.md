# 04 AI Object Counter

Use the AI camera to detect and count three everyday objects: mice, keyboards, and cell phones. Each new appearance increases the matching counter by one, and online TTS announces the object name.

## Learning Goals

- Filter object-detection results by class.
- Count detection events instead of video frames.
- Use state to prevent the same object from being counted repeatedly.
- Display live AI results in a Web UI.
- Announce new counting events with text-to-speech.

## Hardware Requirements

- Arduino UNO Q ×1
- Multimedia Carrier with CSI camera ×1
- USB-C cable ×1
- A mouse, keyboard, and cell phone for testing
- Internet connection for EdgeTTS

The Multimedia Carrier speaker is used for speech. No additional output hardware is required.

> **Note:** The first time a TTS project runs on an UNO Q, App Lab may need half an hour or more to download and prepare the TTS runtime and audio dependencies. Keep the board connected to the Internet. This setup normally happens only once.

## Prerequisites

1. Open Arduino App Lab settings.
2. Enable the external carrier.
3. Configure the camera port as `type1-2lanes`.
4. Reboot the board.

## How to Use

1. Import `04 AI Object Counter.zip` into Arduino App Lab.
2. Click **Run** and open the Web UI.
3. Show one mouse, keyboard, or cell phone to the camera.
4. When the confidence reaches 60%, the corresponding counter increases by one and TTS announces its name.
5. Remove the object completely from the camera view.
6. Show the next object.
7. Click **RESET COUNTS** to return all counters to zero.

For reliable counting, show only one target object at a time.

## How It Works

- CSI Camera → VideoObjectDetection
- Mouse / Keyboard / Cell Phone?
- New appearance? → YES
- Matching counter +1
- TTS announces the object
- Wait for the object to leave

The detector processes many video frames each second. Incrementing a counter on every detected frame would count the same object repeatedly. The program therefore locks each class after it is counted. The class is rearmed only after it has been absent for 10 consecutive detection frames. Speech runs in a background worker so it does not pause camera detection. EdgeTTS does not require an API key; if speech is unavailable, counting and the Web UI continue to work.

## Settings

Edit these values in `python/main.py`:

- `CONFIDENCE_THRESHOLD = 0.60`: minimum confidence required to count.
- `MISSING_FRAMES_TO_REARM = 10`: how long an object must be absent before it can be counted again.
- `TARGETS`: the three classes shown in the Web UI.
- `TTS_VOICE`: voice used for spoken object names.
- `TTS_VOLUME`: speaker volume from 0 to 100.
