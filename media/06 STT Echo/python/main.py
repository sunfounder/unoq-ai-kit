"""Use an external button to control local speech recognition and TTS.

Hold the button to record. Release it to stop recording, recognize
the speech locally, and repeat the recognized sentence aloud.
"""

# import os
import time

from arduino.app_utils import Bridge

from sunfounder_stt import STT
from sunfounder_tts import EdgeTTS

# os.makedirs("./audio_output", exist_ok=True)

BUTTON_RPC = "button_read"
POLL_INTERVAL = 0.05
MIN_RECORDING_TIME = 0.5
AUDIO_OUTPUT_DIR = "/app/audio_output"





tts = EdgeTTS(gain=0.4)
tts.set_voice("en-US-JennyNeural")

print("Preparing the audio input...", flush=True)
stt = STT(type="local_fast", language="en")

print("STT Echo is ready.", flush=True)
print("Hold the button and speak. Release it to recognize and repeat.", flush=True)

last_state = 0
recording = False
recording_started_at = 0.0

try:
    while True:
        state = int(Bridge.call(BUTTON_RPC, ""))

        # Button pressed: start recording.
        if state == 1 and last_state == 0 and not recording:
            print("\nListening...", flush=True)
            stt.start_listening()
            recording = True
            recording_started_at = time.monotonic()

        # Button released: stop recording, recognize, and speak.
        elif state == 0 and last_state == 1 and recording:
            recording_time = time.monotonic() - recording_started_at

            if recording_time < MIN_RECORDING_TIME:
                time.sleep(MIN_RECORDING_TIME - recording_time)

            print("Recognizing...", flush=True)
            stt.stop_listening()
            text = stt.get_result()

            if text and text.strip():
                text = text.strip()
            
                print(f"You said: {text}")
            
                tts.say(text)
            else:
                print("No speech detected.", flush=True)

            recording = False

        last_state = state
        time.sleep(POLL_INTERVAL)

except KeyboardInterrupt:
    if recording:
        stt.stop_listening()
    print("\nProgram stopped.", flush=True)
