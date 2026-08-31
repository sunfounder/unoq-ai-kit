"""03 Voice Recorder

D2: press once to start recording, press again to stop and save.
D3: press once to play the latest recording, press again to stop playback.
"""

import time

from arduino.app_utils import Bridge
from sunfounder_stt import STT
from sunfounder_tts import EdgeTTS

RECORD_BUTTON_RPC = "record_button_read"
PLAY_BUTTON_RPC = "play_button_read"
POLL_INTERVAL = 0.05
AUDIO_FILE = "/app/audio_shared/stt_last.wav"

print("=== Voice Recorder ===", flush=True)
print("D2: Record / Stop Recording", flush=True)
print("D3: Play / Stop Playback", flush=True)

# STT brick is used only for microphone recording in this lesson.
stt = STT(type="online", language="en")

# TTS brick owns the speaker output; no TTS synthesis is used here.
tts = EdgeTTS()
tts.set_volume(50)

recording = False
has_recording = False

last_record_button = 0
last_play_button = 0

print("Ready.", flush=True)

try:
    while True:
        record_button = int(Bridge.call(RECORD_BUTTON_RPC, ""))
        play_button = int(Bridge.call(PLAY_BUTTON_RPC, ""))

        # D2: toggle Record / Stop Recording on each new press.
        if record_button == 1 and last_record_button == 0:
            if not recording:
                # Do not record while the speaker is playing.
                try:
                    tts.stop_audio()
                except Exception:
                    pass

                try:
                    stt.start_recording()
                    recording = True
                    print("Recording...", flush=True)
                except Exception as error:
                    print(f"Record start error: {error}", flush=True)

            else:
                try:
                    stt.stop_recording(AUDIO_FILE)
                    recording = False
                    has_recording = True
                    print("Recording saved.", flush=True)
                except Exception as error:
                    recording = False
                    print(f"Record stop error: {error}", flush=True)

        # D3: toggle Play / Stop Playback on each new press.
        if play_button == 1 and last_play_button == 0:
            if recording:
                print("Stop recording before playback.", flush=True)

            elif not has_recording:
                print("No recording yet. Press D2 to record first.", flush=True)

            else:
                try:
                    state = tts.get_playback_state()

                    if state in ("playing", "paused"):
                        tts.stop_audio()
                        print("Playback stopped.", flush=True)
                    else:
                        tts.play_audio(AUDIO_FILE)
                        print("Playing...", flush=True)

                except Exception as error:
                    print(f"Playback error: {error}", flush=True)

        last_record_button = record_button
        last_play_button = play_button

        time.sleep(POLL_INTERVAL)

except KeyboardInterrupt:
    if recording:
        try:
            stt.stop_recording(AUDIO_FILE)
        except Exception:
            pass

    try:
        tts.stop_audio()
    except Exception:
        pass

    print("Program stopped.", flush=True)
