# SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
#
# SPDX-License-Identifier: MPL-2.0

"""
Gesture Control — control hardware with hand gestures.

The hand-gesture model recognizes four gestures:
  - good  (thumbs-up)   → RGB LED green + "Great!"
  - peace (V-sign)      → take a photo
  - five  (open hand)   → pan-tilt returns to the center
  - neut  (fist)        → RGB LED off (standby)

TTS feedback uses EdgeTTS (Internet required, no API key).
"""

from datetime import UTC, datetime
import os
import queue
import threading
import time
from pathlib import Path

import cv2

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

# Hand-gesture detection
detection = VideoObjectDetection(
    camera,
    confidence=0.5,
    debounce_sec=0.3,
)

# ── Gesture mapping ───────────────────────────────────────
# Label → (display name, RGB color, spoken feedback)
GESTURE_ACTIONS = {
    "good": ("Thumbs up", (0, 255, 0), "Great!"),
    "peace": ("V-sign", None, "Cheese!"),
    "five": ("Open hand", (0, 128, 255), "Back to the center."),
    "neut": ("Fist", (0, 0, 0), None),
}

PHOTO_DIR = Path("/app/photos")
PHOTO_DIR.mkdir(parents=True, exist_ok=True)

# ── State ────────────────────────────────────────────────
last_gesture = None
last_gesture_time = 0.0
GESTURE_LOST_TIMEOUT = 2.0  # seconds before resetting the action state
state_lock = threading.Lock()

# TTS runs in a background worker so detection stays responsive
speech_queue = queue.Queue()


def speech_worker():
    """Play queued messages through EdgeTTS."""
    try:
        os.makedirs("./audio_output", exist_ok=True)
        os.makedirs("/app/audio_output", exist_ok=True)

        tts = EdgeTTS()
        tts.set_voice("en-US-JennyNeural")
        tts.set_volume(50)

        print("EdgeTTS ready — Internet required, no API key needed.")

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
    """Queue a message for speech without blocking detection."""
    if text:
        speech_queue.put(str(text))


def next_photo_path():
    """Return the next unused photo filename."""
    index = 1

    while True:
        path = PHOTO_DIR / f"gesture_{index:03d}.jpg"

        if not path.exists():
            return path

        index += 1


def take_photo():
    """Capture and save one photo."""
    try:
        frame = camera.capture()
        frame = cv2.flip(frame, 0)
    except Exception as error:
        print(f"Photo capture error: {type(error).__name__}: {error}")
        return None

    if frame is None:
        print("Photo capture returned no frame.")
        return None

    photo_path = next_photo_path()

    if cv2.imwrite(str(photo_path), frame):
        print(f"Photo saved: photos/{photo_path.name}")
        return photo_path.name

    print("Failed to save photo.")
    return None


def run_action(label):
    """Run the physical action for a recognized gesture."""
    display_name, color, feedback = GESTURE_ACTIONS[label]

    if label == "peace":
        photo_name = take_photo()

        if photo_name:
            speak("Cheese!")
            ui.send_message("gesture_action", {
                "gesture": display_name,
                "action": "photo",
                "photo": photo_name,
                "timestamp": datetime.now(UTC).isoformat(),
            })
        return

    if label == "five":
        Bridge.call("center_pan_tilt", "")
    elif color is not None:
        r, g, b = color
        Bridge.call("set_rgb_color", r, g, b)

    if feedback:
        speak(feedback)

    ui.send_message("gesture_action", {
        "gesture": display_name,
        "action": "center" if label == "five" else "rgb",
        "timestamp": datetime.now(UTC).isoformat(),
    })


def send_detections(detections: dict):
    """React to the most confident gesture in the current frame."""
    global last_gesture, last_gesture_time

    best_label = None
    best_confidence = 0.0

    for class_name, instances in detections.items():
        if class_name not in GESTURE_ACTIONS:
            continue

        for instance in instances:
            confidence = float(instance.get("confidence", 0.0))
            if confidence > best_confidence:
                best_label = class_name
                best_confidence = confidence

    if best_label is None:
        return

    is_new_gesture = False

    with state_lock:
        last_gesture_time = time.monotonic()

        if best_label != last_gesture:
            last_gesture = best_label
            is_new_gesture = True

    if is_new_gesture:
        run_action(best_label)


def reset_when_gesture_is_lost():
    """Turn the LED off after no gesture has been seen for a while."""
    global last_gesture

    while True:
        should_reset = False

        with state_lock:
            if last_gesture is not None:
                elapsed = time.monotonic() - last_gesture_time

                if elapsed >= GESTURE_LOST_TIMEOUT:
                    last_gesture = None
                    should_reset = True

        if should_reset:
            Bridge.call("set_rgb_color", 0, 0, 0)

            ui.send_message("gesture_action", {
                "gesture": "None",
                "action": "standby",
                "timestamp": datetime.now(UTC).isoformat(),
            })

        time.sleep(0.2)


detection.on_detect_all(send_detections)

threading.Thread(target=speech_worker, daemon=True).start()
threading.Thread(target=reset_when_gesture_is_lost, daemon=True).start()

print("Gesture Control running — show your hand to the camera.")

App.run()
