"""AI Gesture Light — use hand gestures to control one LED."""

import threading
import time

from arduino.app_utils import App, Bridge
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from arduino.app_bricks.web_ui import WebUI
from arduino.app_peripherals.camera import Camera


CONFIDENCE_THRESHOLD = 0.25
GESTURE_LOST_TIMEOUT = 2.0
FLIP_IMAGE = True

GESTURE_NAMES = {
    "good": "Thumbs up",
    "neut": "Fist",
    "five": "Open hand",
    "peace": "V-sign",
}

ui = WebUI()
state_lock = threading.Lock()
last_gesture = None
last_gesture_time = 0.0


def set_led(state):
    """Turn the external LED on or off through Bridge."""
    Bridge.call("set_led", 1 if state else 0)


def send_result(label, confidence, action):
    ui.send_message("gesture_result", {
        "gesture": GESTURE_NAMES.get(label, "None"),
        "confidence": round(confidence * 100),
        "action": action,
    })


def best_gesture(detections):
    """Return the strongest supported model label."""
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


def on_detections(detections):
    """Display every supported gesture and act only when it changes."""
    global last_gesture, last_gesture_time

    label, confidence = best_gesture(detections)
    if label is None:
        return

    with state_lock:
        last_gesture_time = time.monotonic()
        if label == last_gesture:
            return
        last_gesture = label

    if label == "good":
        set_led(True)
        action = "LED ON"
    elif label == "neut":
        set_led(False)
        action = "LED OFF"
    else:
        action = "Gesture displayed"

    print(
        f"[GESTURE] {GESTURE_NAMES[label]} — {confidence * 100:.0f}% — {action}",
        flush=True,
    )
    send_result(label, confidence, action)


def reset_when_gesture_is_lost():
    """Return the webpage to waiting after the hand leaves the camera."""
    global last_gesture

    while True:
        should_reset = False

        with state_lock:
            if (
                last_gesture is not None
                and time.monotonic() - last_gesture_time >= GESTURE_LOST_TIMEOUT
            ):
                last_gesture = None
                should_reset = True

        if should_reset:
            send_result("", 0.0, "Show a gesture")

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

threading.Thread(target=reset_when_gesture_is_lost, daemon=True).start()

print("AI Gesture Light is running — show your hand to the camera.", flush=True)
App.run()
