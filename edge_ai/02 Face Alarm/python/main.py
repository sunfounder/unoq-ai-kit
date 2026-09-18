# SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
#
# SPDX-License-Identifier: MPL-2.0

"""
Face Alarm — sound a buzzer when a face is detected.

When the camera sees a face, Python tells the sketch to turn on
the buzzer via Bridge. When the face disappears, the buzzer stops.
This is the first time AI controls physical hardware.
"""

import threading
import time
from datetime import datetime, UTC

from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from arduino.app_peripherals.camera import Camera

ui = WebUI()

camera = Camera(adjustments=lambda frame: frame[::-1, :])
camera.start()

detection = VideoObjectDetection(
    camera,
    confidence=0.5,
    debounce_sec=0.5,
)

face_visible = False
last_face_time = 0.0
face_lock = threading.Lock()
FACE_LOST_TIMEOUT = 2.0  # seconds before turning off alarm


def face_detected():
    """Called by the brick every time a face is seen."""
    global face_visible, last_face_time

    with face_lock:
        last_face_time = time.monotonic()

        if face_visible:
            return  # Already alarming, just refresh the timer

        face_visible = True

    # First time we see a face → activate the buzzer
    Bridge.call("alarm_on")

    ui.send_message("face_status", {
        "detected": True,
        "text": "Face detected — Alarm ON",
        "timestamp": datetime.now(UTC).isoformat(),
    })


def monitor_face():
    """Background thread: turn off alarm if face is lost for too long."""
    global face_visible

    while True:
        should_off = False

        with face_lock:
            if face_visible:
                elapsed = time.monotonic() - last_face_time
                if elapsed >= FACE_LOST_TIMEOUT:
                    face_visible = False
                    should_off = True

        if should_off:
            Bridge.call("alarm_off")

            ui.send_message("face_status", {
                "detected": False,
                "text": "No face — Alarm OFF",
                "timestamp": datetime.now(UTC).isoformat(),
            })

        time.sleep(0.2)


detection.on_detect("face", face_detected)

# Start background monitor thread
status_thread = threading.Thread(target=monitor_face, daemon=True)
status_thread.start()

print("🚨 Face Alarm running — show your face to the camera!")

App.run()
