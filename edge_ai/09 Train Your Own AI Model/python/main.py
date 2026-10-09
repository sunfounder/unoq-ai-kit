# SPDX-FileCopyrightText: Copyright (C) SunFounder
#
# SPDX-License-Identifier: MPL-2.0

"""09 Train Your Own AI Model - a test bench for the model you train.

This app is deliberately model-agnostic: it runs whatever image-classification
model is selected in the Video Image Classification brick's configuration, from
the built-in general model to a model you train yourself in Edge Impulse
Studio. Nothing in this file names a class, so a model that knows "apple"
and "banana" behaves exactly like one that knows eighty everyday objects.

For every frame that comes back from the model the app:

* lists what the model sees right now, with a confidence for each label
* adds the result to a per-class total for the whole session
* keeps a session timer running, so you can judge how steady the model is
"""

import threading
import time

from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_imageclassification import VideoImageClassification
from arduino.app_peripherals.camera import Camera

# Roughly how often the browser is refreshed, in seconds.
SEND_INTERVAL = 0.4

ui = WebUI()

# The CSI camera is mounted upside down in this kit, so every frame is
# flipped before either the model or the preview sees it.
camera = Camera(adjustments=lambda frame: frame[::-1, :])
camera.start()

# No model is named here on purpose - the brick uses whichever model is
# selected in its Brick Configuration.
classification = VideoImageClassification(camera, confidence=0.4, debounce_sec=0.5)

state_lock = threading.Lock()
started_at = time.monotonic()
latest_objects = []
session_totals = {}
session_detections = 0
last_sent = 0.0
last_logged = None


def snapshot():
    """Build the message that goes to the browser."""
    elapsed = time.monotonic() - started_at

    with state_lock:
        objects = list(latest_objects)
        totals = [
            {"object": name, "count": count}
            for name, count in sorted(session_totals.items(), key=lambda item: -item[1])
        ]
        detections = session_detections
        classes = len(session_totals)

    return {
        "objects": objects,
        "totals": totals,
        "detections": detections,
        "classes": classes,
        "minutes": int(elapsed // 60),
        "seconds": int(elapsed % 60),
    }


def push(force=False):
    """Send the current view to the browser, rate limited."""
    global last_sent

    now = time.monotonic()
    if not force and now - last_sent < SEND_INTERVAL:
        return
    last_sent = now

    ui.send_message("model_report", snapshot())


def report(results: dict):
    """Called by the brick for every frame the model has been through.

    ``results`` maps each label the model recognised in that frame to its
    confidence, for example ``{"card reader": 0.98}``.
    """
    global latest_objects, session_detections, last_logged

    labels = []
    with state_lock:
        for class_name, confidence in results.items():
            session_totals[class_name] = session_totals.get(class_name, 0) + 1
            session_detections += 1
            labels.append({
                "object": class_name,
                "confidence": round(float(confidence) * 100),
            })
        latest_objects = sorted(labels, key=lambda item: -item["confidence"])
        top = max(results.items(), key=lambda item: item[1], default=None)
        if top and top[0] != last_logged:
            last_logged = top[0]
            print("[MODEL] %s (%.0f%%)" % (top[0], float(top[1]) * 100))

    push()


def loop():
    """Heartbeat: keeps the timer and the empty state alive on the page."""
    push()
    time.sleep(0.25)


classification.on_detect_all(report)

print("Train Your Own AI Model running - open the Web UI.")

App.run(user_loop=loop)
