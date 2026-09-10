# SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
#
# SPDX-License-Identifier: MPL-2.0

"""
Face Tracking Camera with Online TTS

When a face is detected for the first time, the board greets
"Nice to meet you." and starts following the face. The pan and tilt
servos move to keep the face centered in the frame.

When the face disappears for 2.5 seconds, the pan-tilt returns to
the center and the next face triggers a new greeting.

The greeting uses EdgeTTS:
- Internet access is required.
- No API key is required.
"""

from datetime import UTC, datetime
import queue
import threading
import time

from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from arduino.app_peripherals.camera import Camera
from sunfounder_tts import EdgeTTS


# Custom web interface
ui = WebUI()

# CSI camera
camera = Camera(adjustments=lambda frame: frame[::-1, :])
camera.start()

# Face detection
detection = VideoObjectDetection(
    camera,
    confidence=0.5,
    debounce_sec=0.1,
)

# ── Tracking configuration ────────────────────────────────
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
DEAD_ZONE_RATIO = 0.10   # Ignore small offsets to reduce servo jitter.
FACE_LOST_TIMEOUT = 2.5  # Seconds before returning to the center.

# ── Greeting configuration ────────────────────────────────
GREETING_TEXT = "Nice to meet you."
GREETING_VOICE = "en-US-JennyNeural"
GREETING_VOLUME = 50

# ── Tracking state ────────────────────────────────────────
face_visible = False
last_face_time = 0.0
state_lock = threading.Lock()

# TTS runs in a background worker so tracking stays responsive
speech_queue = queue.Queue()


def speech_worker():
    """Play queued messages through EdgeTTS."""
    try:
        tts = EdgeTTS()
        tts.set_voice(GREETING_VOICE)
        tts.set_volume(GREETING_VOLUME)

        print("EdgeTTS ready.")

        while True:
            text = speech_queue.get()

            try:
                tts.say(text)
            except Exception as error:
                print(f"TTS error: {type(error).__name__}: {error}")
            finally:
                speech_queue.task_done()

    except Exception as error:
        print(f"TTS startup failed: {type(error).__name__}: {error}")


def speak(text):
    """Queue a message for speech without blocking tracking."""
    if text:
        speech_queue.put(str(text))


def box_center(instance):
    """Return the (x, y) center of a detection box, or None.

    App Lab normally reports ``bounding_box_xyxy`` as the top-left
    and bottom-right coordinates. Older alternative formats are kept
    as fallbacks.
    """
    bbox_xyxy = instance.get("bounding_box_xyxy")

    if isinstance(bbox_xyxy, (list, tuple)) and len(bbox_xyxy) >= 4:
        x1, y1, x2, y2 = bbox_xyxy[:4]
        return (x1 + x2) / 2.0, (y1 + y2) / 2.0

    bbox = instance.get("bbox") or instance.get("box")

    if isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
        x, y, w, h = bbox[0], bbox[1], bbox[2], bbox[3]
    elif all(key in instance for key in ("x", "y", "width", "height")):
        x = instance["x"]
        y = instance["y"]
        w = instance["width"]
        h = instance["height"]
    else:
        return None

    if x + w <= 1.0 and y + h <= 1.0:
        # Normalized coordinates → scale to pixels.
        x, w = x * FRAME_WIDTH, w * FRAME_WIDTH
        y, h = y * FRAME_HEIGHT, h * FRAME_HEIGHT

    return x + w / 2.0, y + h / 2.0


def as_detection_list(value):
    """Normalize one detection dictionary or a list of dictionaries."""
    if isinstance(value, dict):
        return [value]

    if isinstance(value, (list, tuple)):
        return [item for item in value if isinstance(item, dict)]

    return []


def track_face(center_x, center_y):
    """Move both servos when the face drifts outside the dead zone."""
    offset_x = center_x - FRAME_WIDTH / 2.0
    offset_y = center_y - FRAME_HEIGHT / 2.0

    pan_direction = 0
    tilt_direction = 0

    if abs(offset_x) >= FRAME_WIDTH * DEAD_ZONE_RATIO:
        pan_direction = 1 if offset_x > 0 else -1

    if abs(offset_y) >= FRAME_HEIGHT * DEAD_ZONE_RATIO:
        tilt_direction = 1 if offset_y > 0 else -1

    if pan_direction:
        Bridge.call("pan_step", pan_direction)

    if tilt_direction:
        Bridge.call("tilt_step", tilt_direction)


def send_detections(detections: dict):
    """Follow the most confident face in the current frame."""
    global face_visible, last_face_time

    best_center = None
    best_confidence = 0.0

    for instance in as_detection_list(detections.get("face")):
        confidence = float(instance.get("confidence", 0.0))

        if confidence > best_confidence:
            best_center = box_center(instance)
            best_confidence = confidence

    if best_confidence <= 0:
        return

    is_new_face = False

    with state_lock:
        last_face_time = time.monotonic()

        if not face_visible:
            # Face reappeared → greet again and start following.
            face_visible = True
            is_new_face = True

    if is_new_face:
        speak(GREETING_TEXT)

        ui.send_message("face_status", {
            "detected": True,
            "text": "Nice to meet you!",
            "timestamp": datetime.now(UTC).isoformat(),
        })

    # Greeting and status still work even if a future detector version
    # changes its bounding-box format.
    if best_center is not None:
        track_face(*best_center)


def monitor_face_status():
    """Return the pan-tilt to center when the face has been lost."""
    global face_visible

    while True:
        should_center = False

        with state_lock:
            if face_visible:
                elapsed = time.monotonic() - last_face_time

                if elapsed >= FACE_LOST_TIMEOUT:
                    face_visible = False
                    should_center = True

        if should_center:
            Bridge.call("center_pan_tilt", "")

            ui.send_message("face_status", {
                "detected": False,
                "text": "Looking for a face",
                "timestamp": datetime.now(UTC).isoformat(),
            })

        time.sleep(0.2)


detection.on_detect_all(send_detections)

threading.Thread(target=speech_worker, daemon=True).start()
threading.Thread(target=monitor_face_status, daemon=True).start()

print("Face Tracking Camera with TTS is running.")

App.run()
