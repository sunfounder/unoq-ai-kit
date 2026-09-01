"""Control a pan-tilt with spoken commands and provide TTS feedback.

Hold the external button to record. Release it to recognize the speech,
move the corresponding servo to a fixed angle, and speak a confirmation.
"""

import time
from typing import Optional, Tuple

from arduino.app_utils import Bridge

from sunfounder_stt import STT
from sunfounder_tts import EdgeTTS


BUTTON_RPC = "button_read"
POLL_INTERVAL = 0.05
MIN_RECORDING_TIME = 0.5
AUDIO_OUTPUT_DIR = "/app/audio_output"

# Each entry is: phrases, Bridge RPC, spoken feedback, console action.
COMMANDS = (
    (("turn left", "look left", "left"), "pan_left", "Turning left.", "Turning left."),
    (("turn right", "look right", "right"), "pan_right", "Turning right.", "Turning right."),
    (("look up", "turn up", "up"), "tilt_up", "Looking up.", "Looking up."),
    (("look down", "turn down", "down"), "tilt_down", "Looking down.", "Looking down."),
    (("center", "centre", "look forward", "return to center"), "center", "Returning to center.", "Returning to center."),
)


def match_command(text: str) -> Optional[Tuple[str, str, str]]:
    """Return the RPC, feedback, and console action for recognized text."""
    normalized = " ".join(text.lower().strip().split())

    for phrases, rpc_name, feedback, action in COMMANDS:
        if any(phrase in normalized for phrase in phrases):
            return rpc_name, feedback, action

    return None




print("Preparing the audio input and output...", flush=True)


stt = STT(type="local_fast", language="en")
tts = EdgeTTS()
tts.set_voice("en-US-JennyNeural")
tts.set_volume(50)

print("Voice-controlled pan-tilt is ready.", flush=True)
print("Supported commands:", flush=True)
print("  Turn left | Turn right | Look up | Look down | Center", flush=True)
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

        # Button released: stop recording and recognize the command.
        elif state == 0 and last_state == 1 and recording:
            recording_time = time.monotonic() - recording_started_at

            if recording_time < MIN_RECORDING_TIME:
                time.sleep(MIN_RECORDING_TIME - recording_time)

            print("Recognizing...", flush=True)
            stt.stop_listening()
            text = stt.get_result()
            if isinstance(text, dict):
                text = text.get("text", "")
            recording = False

            if text and text.strip():
                recognized_text = text.strip()
                print("Recognized:", flush=True)
                print(recognized_text, flush=True)

                command = match_command(recognized_text)

                if command is None:
                    print("Command not recognized.", flush=True)
                    tts.say("Command not recognized.")
                else:
                    rpc_name, feedback, action = command
                    Bridge.call(rpc_name, "")
                    print(action, flush=True)
                    tts.say(feedback)
            else:
                print("No speech recognized.", flush=True)

        last_state = state
        time.sleep(POLL_INTERVAL)

except KeyboardInterrupt:
    if recording:
        stt.stop_listening()
    print("\nProgram stopped.", flush=True)
