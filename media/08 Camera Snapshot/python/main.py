"""Capture and save a photo when the external button is pressed."""

import time
from pathlib import Path

import cv2

from arduino.app_peripherals.camera import Camera
from arduino.app_utils import Bridge


BUTTON_RPC = "button_read"
POLL_INTERVAL = 0.05
PHOTO_DIR = Path("/app/photos")


def next_photo_path() -> Path:
    """Return the next unused photo filename."""
    index = 1

    while True:
        path = PHOTO_DIR / f"photo_{index:03d}.jpg"

        if not path.exists():
            return path

        index += 1


PHOTO_DIR.mkdir(parents=True, exist_ok=True)

print("Initializing camera...", flush=True)
camera = Camera()
camera.start()
time.sleep(1)

print("Camera ready.", flush=True)
print("Press the button to take a photo.", flush=True)

last_state = 0

try:
    while True:
        state = int(Bridge.call(BUTTON_RPC, ""))

        # Capture once when the button changes from released to pressed.
        if state == 1 and last_state == 0:
            print("\nCapturing...", flush=True)

            frame = camera.capture()

            # Flip the image vertically.
            frame = cv2.flip(frame, 0)

            photo_path = next_photo_path()

            if cv2.imwrite(str(photo_path), frame):
                print(
                    f"Photo saved: photos/{photo_path.name}",
                    flush=True,
                )
            else:
                print("Failed to save photo.", flush=True)

        last_state = state
        time.sleep(POLL_INTERVAL)

except KeyboardInterrupt:
    print("\nStopping camera...", flush=True)

finally:
    camera.stop()
    print("Program stopped.", flush=True)
