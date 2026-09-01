# Smart Doorbell: when the sketch reports a button press over Bridge, this
# App saves a visitor photo from the camera, streams a live preview to the
# Web UI, and announces the visitor through the speaker (EdgeTTS).
#
# The button (D2) and buzzer (D5) are handled by the sketch; the camera
# and speaker are the Multimedia Carrier's built-in peripherals.
import base64
import time
from datetime import datetime
from pathlib import Path

import cv2

from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_peripherals.camera import Camera
from sunfounder_tts import EdgeTTS

ui = WebUI()

PHOTO_DIR = Path("/app/photos")
AUDIO_OUTPUT_DIR = Path("/app/audio_output")
PHOTO_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Stream about 5 frames per second to the Web UI.
STREAM_INTERVAL = 0.20
JPEG_QUALITY = 70

latest_frame = None
snapshot_requested = False
announcement_requested = False
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

print("Initializing speaker...", flush=True)
tts = EdgeTTS()
tts.set_voice("en-US-JennyNeural")
tts.set_volume(50)
print("Speaker ready.", flush=True)


def send_frame_to_web(frame):
    # Encode the frame as a base64 JPEG for the browser.
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
    global announcement_requested

    timestamp = datetime.now().strftime("%H:%M:%S")

    print(f"Doorbell pressed at {timestamp}", flush=True)

    ui.send_message(
        "doorbell_event",
        {"time": timestamp},
    )

    # Defer the heavy work (photo + speech) to the App loop.
    snapshot_requested = True
    announcement_requested = True


Bridge.provide("doorbell_pressed", doorbell_pressed)


def loop():
    global latest_frame
    global snapshot_requested
    global announcement_requested
    global last_stream_time

    now = time.monotonic()

    # Keep the live preview flowing to the Web UI.
    if now - last_stream_time >= STREAM_INTERVAL:
        frame = camera.capture()
        frame = cv2.flip(frame, 0)

        latest_frame = frame
        last_stream_time = now

        send_frame_to_web(frame)

    # Save the latest frame as a timestamped visitor photo.
    if snapshot_requested and latest_frame is not None:
        snapshot_requested = False
        save_visitor_photo(latest_frame)

    # Announce the visitor over the speaker.
    if announcement_requested:
        announcement_requested = False
        print("Speaker: Someone is at the door.", flush=True)

        try:
            tts.say("Someone is at the door.")
        except Exception as exc:
            print(f"Speaker error: {exc}", flush=True)

    time.sleep(0.02)


App.run(user_loop=loop)
