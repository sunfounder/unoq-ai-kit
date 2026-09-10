# SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
#
# SPDX-License-Identifier: MPL-2.0

"""
AI Object Color Light

The object-detection model runs locally on the UNO Q. When a mapped
object is detected, the application sends a color code to the sketch
and updates the custom Web UI.
"""

from datetime import datetime, UTC
import threading
import time

from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from arduino.app_peripherals.camera import Camera

ui = WebUI()

camera = Camera(adjustments=lambda frame: frame[::-1, :])
camera.start()

detection = VideoObjectDetection(camera, confidence=0.45, debounce_sec=0.3)

# Object name: (color code, display name, HEX color)
OBJECT_COLORS = {
    "apple": (1, "Red", "#ef5350"),
    "banana": (2, "Yellow", "#fbc02d"),
    "orange": (3, "Orange", "#fb8c00"),
    "broccoli": (4, "Green", "#43a047"),
    "bottle": (5, "Blue", "#29a3d9"),
    "person": (6, "White", "#ffffff"),
}

NO_OBJECT_TIMEOUT = 2.0
last_detection_time = 0.0
current_object = None
state_lock = threading.Lock()


def set_color(color_code: int):
    """Send a color code to the Arduino sketch."""
    Bridge.call("set_color", color_code)


def publish_state(object_name, color_name, hex_color, confidence=0):
    ui.send_message(
        "object_color",
        message={
            "object": object_name,
            "color": color_name,
            "hex": hex_color,
            "confidence": confidence,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


def send_detections(detections: dict):
    """Choose the highest-confidence mapped object in the current frame."""
    global last_detection_time, current_object

    best_object = None
    best_confidence = 0.0

    for class_name, instances in detections.items():
        if class_name not in OBJECT_COLORS:
            continue

        for instance in instances:
            confidence = float(instance.get("confidence", 0.0))
            if confidence > best_confidence:
                best_object = class_name
                best_confidence = confidence

    if best_object is None:
        return

    color_code, color_name, hex_color = OBJECT_COLORS[best_object]

    with state_lock:
        last_detection_time = time.monotonic()
        changed = best_object != current_object
        current_object = best_object

    if changed:
        set_color(color_code)

    publish_state(
        best_object,
        color_name,
        hex_color,
        round(best_confidence * 100),
    )


def clear_when_object_is_lost():
    """Turn the LED off after no mapped object has been seen for a while."""
    global current_object

    while True:
        should_clear = False

        with state_lock:
            if (
                current_object is not None
                and time.monotonic() - last_detection_time > NO_OBJECT_TIMEOUT
            ):
                current_object = None
                should_clear = True

        if should_clear:
            set_color(0)
            publish_state("No mapped object", "Off", "#dfe6e9", 0)

        time.sleep(0.2)


detection.on_detect_all(send_detections)

threading.Thread(target=clear_when_object_is_lost, daemon=True).start()

App.run()
