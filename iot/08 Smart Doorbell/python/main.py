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

STREAM_INTERVAL = 0.20
JPEG_QUALITY = 70

latest_frame = None
snapshot_requested = False
last_stream_time = 0.0


def next_photo_path():
    index = 1
    while True:
        path = PHOTO_DIR / f"visitor_{index:03d}.jpg"
        if not path.exists():
            return path
        index += 1


print("Initializing camera...", flush=True)

camera = Camera()
camera.start()
time.sleep(1)

print("Camera ready.", flush=True)


def send_frame_to_web(frame):
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
        {"image": image_base64},
    )


def save_visitor_photo(frame):
    if frame is None:
        return

    photo_path = next_photo_path()

    if not cv2.imwrite(str(photo_path), frame):
        print("Failed to save visitor photo.", flush=True)
        return

    timestamp = datetime.now().strftime("%H:%M:%S")

    print(
        f"Visitor photo saved: photos/{photo_path.name}",
        flush=True,
    )

    ui.send_message(
        "visitor_photo",
        {
            "filename": photo_path.name,
            "time": timestamp,
        },
    )


def doorbell_pressed():
    global snapshot_requested

    timestamp = datetime.now().strftime("%H:%M:%S")

    print(f"Doorbell pressed at {timestamp}", flush=True)

    ui.send_message(
        "doorbell_event",
        {"time": timestamp},
    )

    snapshot_requested = True


Bridge.provide("doorbell_pressed", doorbell_pressed)


def loop():
    global latest_frame
    global snapshot_requested
    global last_stream_time

    now = time.monotonic()

    if now - last_stream_time >= STREAM_INTERVAL:
        frame = camera.capture()
        frame = cv2.flip(frame, 0)

        latest_frame = frame
        last_stream_time = now

        send_frame_to_web(frame)

    if snapshot_requested and latest_frame is not None:
        snapshot_requested = False
        save_visitor_photo(latest_frame)

    time.sleep(0.02)


App.run(user_loop=loop)
