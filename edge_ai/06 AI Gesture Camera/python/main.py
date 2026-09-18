"""AI Gesture Camera — control camera tilt and take photos with gestures."""

from datetime import UTC, datetime
import os
import queue
import threading
import time
from pathlib import Path

import cv2

from arduino.app_utils import App, Bridge
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from arduino.app_bricks.web_ui import WebUI
from arduino.app_peripherals.camera import Camera
from sunfounder_tts import EdgeTTS


CONFIDENCE_THRESHOLD = 0.25
STABLE_SECONDS = 0.6
MIN_ACTION_INTERVAL = 5.0
REARM_NO_GESTURE_SECONDS = 3.0
FLIP_IMAGE = True

GESTURE_NAMES = {
    "good": "Thumbs up",
    "neut": "Fist",
    "five": "Open hand",
    "peace": "V-sign",
}

ui = WebUI()
state_lock = threading.Lock()
action_queue = queue.Queue(maxsize=1)

gesture_armed = True
candidate_gesture = None
candidate_since = 0.0
last_detection_time = 0.0
last_action_time = 0.0

photo_dir = Path("/app/photos")
photo_dir.mkdir(parents=True, exist_ok=True)


def send_result(label, confidence, action):
    ui.send_message("gesture_result", {
        "gesture": GESTURE_NAMES.get(label, "None"),
        "confidence": round(confidence * 100),
        "action": action,
        "timestamp": datetime.now(UTC).isoformat(),
    })


def best_gesture(detections):
    best_label = None
    best_confidence = 0.0

    for label, instances in detections.items():
        if label not in GESTURE_NAMES:
            continue

        for instance in instances:
            confidence = float(instance.get("confidence", 0.0))
            if confidence > 1:
                confidence /= 100
            if confidence > best_confidence:
                best_label = label
                best_confidence = confidence

    if best_confidence < CONFIDENCE_THRESHOLD:
        return None, 0.0
    return best_label, best_confidence


def next_photo_path():
    index = 1
    while True:
        path = photo_dir / f"gesture_{index:03d}.jpg"
        if not path.exists():
            return path
        index += 1


def take_photo():
    """Capture one frame without performing the operation in the AI callback."""
    frame = camera.capture()
    if frame is None:
        return None

    # Camera adjustments already rotate the image used by the model and preview.
    path = next_photo_path()
    if cv2.imwrite(str(path), frame):
        return path.name
    return None


def action_worker():
    """Run hardware, photo, and TTS actions sequentially in one worker."""
    os.makedirs("/app/audio_output", exist_ok=True)

    try:
        tts = EdgeTTS()
        tts.set_voice("en-US-JennyNeural")
        tts.set_volume(40)
        print("[TTS] Ready.", flush=True)
    except Exception as error:
        tts = None
        print(f"[TTS ERROR] {type(error).__name__}: {error}", flush=True)

    while True:
        label, confidence = action_queue.get()

        try:
            if label == "good":
                angle = Bridge.call("tilt_up", "")
                if int(angle) <= 60:
                    action = "Camera reached the highest position (60 degrees)"
                    speech = "Highest position reached. I cannot move up any further."
                else:
                    action = f"Camera moved up to {angle} degrees"
                    speech = "Moving up."
            elif label == "neut":
                angle = Bridge.call("tilt_down", "")
                if int(angle) >= 110:
                    action = "Camera reached the lowest position (110 degrees)"
                    speech = "Lowest position reached. I cannot move down any further."
                else:
                    action = f"Camera moved down to {angle} degrees"
                    speech = "Moving down."
            elif label == "five":
                Bridge.call("center_pan_tilt", "")
                action = "Pan-tilt centered"
                speech = "Back to the center."
            else:
                photo_name = take_photo()
                if photo_name:
                    action = f"Photo saved: {photo_name}"
                    speech = "Photo taken."
                else:
                    action = "Photo failed"
                    speech = "I could not take the photo."

            print(
                f"[GESTURE] {GESTURE_NAMES[label]} — "
                f"{confidence * 100:.0f}% — {action}",
                flush=True,
            )
            send_result(label, confidence, f"{action} — remove your hand")

            if tts is not None:
                try:
                    tts.say(speech)
                except Exception as error:
                    print(f"[TTS ERROR] {type(error).__name__}: {error}", flush=True)

        except Exception as error:
            print(f"[ACTION ERROR] {type(error).__name__}: {error}", flush=True)
            send_result(label, confidence, "Action failed")
        finally:
            action_queue.task_done()


def on_detections(detections):
    """Require one stable gesture, then lock until the hand is removed."""
    global gesture_armed, candidate_gesture, candidate_since
    global last_detection_time, last_action_time

    label, confidence = best_gesture(detections)
    if label is None:
        return

    now = time.monotonic()

    with state_lock:
        last_detection_time = now

        if not gesture_armed or now - last_action_time < MIN_ACTION_INTERVAL:
            return

        if label != candidate_gesture:
            candidate_gesture = label
            candidate_since = now
            return

        if now - candidate_since < STABLE_SECONDS:
            return

        gesture_armed = False
        candidate_gesture = None
        last_action_time = now

    try:
        action_queue.put_nowait((label, confidence))
    except queue.Full:
        print("[BUSY] Previous gesture action is still running.", flush=True)


def rearm_after_hand_is_removed():
    """Unlock only after a minimum delay and three seconds with no gesture."""
    global gesture_armed, candidate_gesture

    while True:
        should_rearm = False
        now = time.monotonic()

        with state_lock:
            if (
                not gesture_armed
                and now - last_action_time >= MIN_ACTION_INTERVAL
                and now - last_detection_time >= REARM_NO_GESTURE_SECONDS
            ):
                gesture_armed = True
                candidate_gesture = None
                should_rearm = True

        if should_rearm:
            print("[READY] Show the next gesture.", flush=True)
            send_result("", 0.0, "Ready — show a gesture")

        time.sleep(0.2)


if FLIP_IMAGE:
    camera = Camera(adjustments=lambda frame: frame[::-1, :])
else:
    camera = Camera()

camera.start()

detection = VideoObjectDetection(
    camera,
    confidence=CONFIDENCE_THRESHOLD,
    debounce_sec=0.2,
)
detection.on_detect_all(on_detections)

threading.Thread(target=action_worker, daemon=True).start()
threading.Thread(target=rearm_after_hand_is_removed, daemon=True).start()

print("AI Gesture Camera is running.", flush=True)
App.run()
