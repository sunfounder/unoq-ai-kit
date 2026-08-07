"""Control a pan-tilt and capture photos using spoken commands."""

# import os
import time
from pathlib import Path
from typing import Callable, Optional

import cv2

from arduino.app_peripherals.camera import Camera
from arduino.app_utils import Bridge

from sunfounder_stt import STT
from sunfounder_tts import EdgeTTS


# os.makedirs("./audio_output", exist_ok=True)

LISTEN_SECONDS = 4
PAUSE_BETWEEN_CYCLES = 0.8

AUDIO_OUTPUT_DIR = Path("/app/audio_output")
PHOTO_DIR = Path("/app/photos")

AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PHOTO_DIR.mkdir(parents=True, exist_ok=True)

print("Preparing audio input and output...", flush=True)


print("Loading local speech recognition...", flush=True)
stt = STT(type="local_fast", language="en")

tts = EdgeTTS(gain=0.4)
tts.set_voice("en-US-JennyNeural")

print("Initializing camera...", flush=True)
camera = Camera()
camera.start()
time.sleep(1)


def next_photo_path() -> Path:
    """Return the next unused photo filename."""
    index = 1

    while True:
        path = PHOTO_DIR / f"photo_{index:03d}.jpg"

        if not path.exists():
            return path

        index += 1


def move_left() -> None:
    Bridge.call("pan_left", "")
    print("Pan: -45°", flush=True)
    tts.say("Turning left.")


def move_right() -> None:
    Bridge.call("pan_right", "")
    print("Pan: 45°", flush=True)
    tts.say("Turning right.")


def move_up() -> None:
    Bridge.call("tilt_up", "")
    print("Tilt: -45°", flush=True)
    tts.say("Looking up.")


def move_down() -> None:
    Bridge.call("tilt_down", "")
    print("Tilt: 45°", flush=True)
    tts.say("Looking down.")


def move_center() -> None:
    Bridge.call("center", "")
    print("Pan: 0°, Tilt: 0°", flush=True)
    tts.say("Returning to center.")


def take_photo() -> None:
    tts.say("Taking a photo.")

    frame = camera.capture()

    # Correct the camera orientation on the pan-tilt mount.
    frame = cv2.flip(frame, 0)

    photo_path = next_photo_path()

    if cv2.imwrite(str(photo_path), frame):
        print(f"Photo saved: photos/{photo_path.name}", flush=True)
        tts.say("Photo saved.")
    else:
        print("Failed to save photo.", flush=True)
        tts.say("Failed to save the photo.")


COMMANDS: tuple[tuple[tuple[str, ...], Callable[[], None]], ...] = (
    (("take a photo", "take photo", "capture a photo", "capture photo"), take_photo),
    (("turn left", "look left", "left"), move_left),
    (("turn right", "look right", "right"), move_right),
    (("look up", "turn up", "up"), move_up),
    (("look down", "turn down", "down"), move_down),
    (("return to center", "look forward", "centre", "center"), move_center),
)


def match_command(text: str) -> Optional[Callable[[], None]]:
    """Return the action that matches the recognized speech."""
    normalized = " ".join(text.lower().strip().split())

    for phrases, action in COMMANDS:
        if any(phrase in normalized for phrase in phrases):
            return action

    return None


print("Voice-controlled camera is ready.", flush=True)
print("Supported commands:", flush=True)
print("  Turn left | Turn right | Look up | Look down | Center | Take photo", flush=True)
print(f"The microphone listens for {LISTEN_SECONDS} seconds each time.", flush=True)

try:
    while True:
        try:
            stt.reset()

            print("\nListening... Please speak.", flush=True)
            stt.start_listening()
            time.sleep(LISTEN_SECONDS)
            stt.stop_listening()

            print("Recognizing...", flush=True)
            text = stt.get_result(timeout=60)
            recognized_text = text.strip() if text else ""

            if not recognized_text:
                print("No speech recognized.", flush=True)
            else:
                print(f"Recognized: {recognized_text}", flush=True)
                action = match_command(recognized_text)

                if action is None:
                    print("Command not recognized.", flush=True)
                    tts.say("Command not recognized.")
                else:
                    action()

            # Wait until TTS playback has finished before listening again.
            time.sleep(PAUSE_BETWEEN_CYCLES)

        except Exception as error:
            print(f"Voice-control cycle error: {error}", flush=True)

            try:
                stt.stop_listening()
            except Exception:
                pass

            time.sleep(2)

except KeyboardInterrupt:
    print("\nStopping...", flush=True)

finally:
    try:
        stt.stop_listening()
    except Exception:
        pass

    camera.stop()
    print("Program stopped.", flush=True)
