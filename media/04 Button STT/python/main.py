"""Use an external button to control local speech recognition.

Hold the button to record. Release it to stop recording and recognize
the recorded speech locally.
"""

# import os
import time

from arduino.app_utils import Bridge
from sunfounder_stt import STT

# os.makedirs("./audio_output", exist_ok=True)

BUTTON_RPC = "button_read"
POLL_INTERVAL = 0.05
MIN_RECORDING_TIME = 0.5
AUDIO_OUTPUT_DIR = "/app/audio_output"


print("Preparing the audio input...", flush=True)
stt = STT(type="local_fast", language="en")

print("Local STT is ready.", flush=True)
print("Hold the button and speak. Release it to recognize.", flush=True)

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

        # Button released: stop recording and recognize the speech.
        elif state == 0 and last_state == 1 and recording:
            recording_time = time.monotonic() - recording_started_at

            if recording_time < MIN_RECORDING_TIME:
                time.sleep(MIN_RECORDING_TIME - recording_time)

            print("Recognizing...", flush=True)
            stt.stop_listening()
            text = stt.get_result()

            if text and text.strip():
                print(f"You said: {text.strip()}", flush=True)

            recording = False

        last_state = state
        time.sleep(POLL_INTERVAL)

except KeyboardInterrupt:
    if recording:
        stt.stop_listening()
    print("\nProgram stopped.", flush=True)
