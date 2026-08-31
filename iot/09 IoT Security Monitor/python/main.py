"""
08 IoT Security Monitor

This project does NOT use any Edge AI or object-detection Brick.

The CSI camera is used as a normal camera:
- capture frames
- send JPEG frames to the Web UI for live preview
- save security snapshots

The MCU handles:
- PIR motion detection on D2
- 10-second motion hold time
- passive buzzer on D5 (tone alarm)
"""

import base64
import time
from datetime import datetime
from pathlib import Path

import cv2

from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_peripherals.camera import Camera

ui = WebUI()

PHOTO_DIR = Path("/app/photos")
PHOTO_DIR.mkdir(parents=True, exist_ok=True)

# Camera preview settings
STREAM_INTERVAL = 0.20       # About 5 FPS
JPEG_QUALITY = 70

# Repeat a snapshot every 2 minutes while motion remains active.
REPEAT_PHOTO_SECONDS = 120.0

motion_active = False
snapshot_requested = False
last_photo_time = 0.0
last_stream_time = 0.0
latest_frame = None


def next_photo_path() -> Path:
    """Return the next unused security photo filename."""
    index = 1

    while True:
        path = PHOTO_DIR / f"security_{index:03d}.jpg"

        if not path.exists():
            return path

        index += 1


print("Initializing camera...", flush=True)

camera = Camera()
camera.start()
time.sleep(1)

print("Camera ready.", flush=True)


def send_frame_to_web(frame):
    """Encode one camera frame as JPEG and send it to the Web UI."""
    success, encoded = cv2.imencode(
        ".jpg",
        frame,
        [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY],
    )

    if not success:
        return

    image_base64 = base64.b64encode(
        encoded.tobytes()
    ).decode("ascii")

    ui.send_message(
        "camera_frame",
        {
            "image": image_base64,
        },
    )


def save_security_photo(frame):
    """Save the current camera frame as a security snapshot."""
    global last_photo_time

    if frame is None:
        print("No camera frame available for snapshot.", flush=True)
        return

    photo_path = next_photo_path()

    if not cv2.imwrite(str(photo_path), frame):
        print("Failed to save photo.", flush=True)
        return

    last_photo_time = time.monotonic()
    timestamp = datetime.now().strftime("%H:%M:%S")

    print(
        f"Photo saved: photos/{photo_path.name}",
        flush=True,
    )

    ui.send_message(
        "security_photo",
        {
            "filename": photo_path.name,
            "time": timestamp,
        },
    )


def motion_state(detected: bool):
    """
    Receive the final latched motion state from the MCU.

    Keep this callback short. Snapshot saving is deferred to the App loop.
    """
    global motion_active, snapshot_requested

    detected = bool(detected)
    motion_active = detected

    print(
        "Motion detected" if detected else "Area clear",
        flush=True,
    )

    ui.send_message(
        "motion_status",
        {
            "detected": detected,
        },
    )

    if detected:
        snapshot_requested = True


Bridge.provide("motion_state", motion_state)


def loop():
    """Capture the live preview and handle requested/periodic snapshots."""
    global latest_frame
    global snapshot_requested
    global last_stream_time

    now = time.monotonic()

    # Capture and stream at about 5 FPS.
    if now - last_stream_time >= STREAM_INTERVAL:
        frame = camera.capture()

        # Match the orientation used by the Camera Snapshot example.
        frame = cv2.flip(frame, 0)

        latest_frame = frame
        last_stream_time = now

        send_frame_to_web(frame)

    # First motion event: save immediately using the latest available frame.
    if snapshot_requested and latest_frame is not None:
        snapshot_requested = False
        save_security_photo(latest_frame)

    # If motion stays active, save another image every 2 minutes.
    elif (
        motion_active
        and latest_frame is not None
        and last_photo_time > 0
        and now - last_photo_time >= REPEAT_PHOTO_SECONDS
    ):
        save_security_photo(latest_frame)

    time.sleep(0.02)


App.run(user_loop=loop)
