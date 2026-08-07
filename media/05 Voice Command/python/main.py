"""Control an RGB LED with spoken color commands.

Hold the button to record. Release it to recognize the command locally.
"""

# import os
import time

from arduino.app_utils import Bridge
from sunfounder_stt import STT

# os.makedirs("./audio_output", exist_ok=True)

BUTTON_RPC = "button_read"
COLOR_RPC = "set_color"
POLL_INTERVAL = 0.05
MIN_RECORDING_TIME = 0.5
AUDIO_OUTPUT_DIR = "/app/audio_output"

SUPPORTED_COLORS = (
    "red",
    "green",
    "blue",
    "yellow",
    "cyan",
    "purple",
    "white",
)


print("Preparing the audio input...", flush=True)
stt = STT(type="local_fast", language="en")

print("Local STT is ready.", flush=True)
print("Say a color, or say 'turn off the light'.", flush=True)
print("Hold the button and speak. Release it to recognize.", flush=True)

last_state = 0
recording = False
recording_started_at = 0.0

try:
    while True:
        state = int(Bridge.call(BUTTON_RPC, ""))

        if state == 1 and last_state == 0 and not recording:
            print("\nListening...", flush=True)
            stt.start_listening()
            recording = True
            recording_started_at = time.monotonic()

        elif state == 0 and last_state == 1 and recording:
            recording_time = time.monotonic() - recording_started_at

            if recording_time < MIN_RECORDING_TIME:
                time.sleep(MIN_RECORDING_TIME - recording_time)

            print("Recognizing...", flush=True)
            stt.stop_listening()
            text = stt.get_result()

            if text and text.strip():
                command = text.strip().lower()
                print(f"You said: {text.strip()}", flush=True)

                selected_color = None

                if "off" in command:
                    selected_color = "off"
                else:
                    for color in SUPPORTED_COLORS:
                        if color in command:
                            selected_color = color
                            break

                if selected_color is None:
                    print(
                        "Try: red, green, blue, yellow, cyan, purple, white, or off.",
                        flush=True,
                    )
                else:
                    Bridge.call(COLOR_RPC, selected_color)

                    if selected_color == "off":
                        print("Light turned off.", flush=True)
                    else:
                        print(f"Light set to {selected_color}.", flush=True)

            recording = False

        last_state = state
        time.sleep(POLL_INTERVAL)

except KeyboardInterrupt:
    if recording:
        stt.stop_listening()

    Bridge.call(COLOR_RPC, "off")
    print("\nProgram stopped.", flush=True)
