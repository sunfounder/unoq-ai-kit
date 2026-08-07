# SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
#
# SPDX-License-Identifier: MPL-2.0

"""
AI Vision Recognition — recognize cup, person, and cell phone.

The VideoObjectDetection brick (with no model restriction) detects
common objects in the camera feed. Detections are sent to the custom
Web UI via socket.io and displayed alongside the live video stream.
"""

from datetime import datetime, UTC
from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from arduino.app_peripherals.camera import Camera

# Serve our custom web interface
ui = WebUI()

# Start the CSI camera
camera = Camera(adjustments=lambda frame: frame[::-1, :])
camera.start()

# Video object detection — general model (detects cup, person, phone, etc.)
detection = VideoObjectDetection(camera, confidence=0.4, debounce_sec=1.0)

# Send all detections to the web UI
def send_detections(detections: dict):
    """Called for every frame with detection results."""
    results = []
    for class_name, instances in detections.items():
        for instance in instances:
            results.append({
                "object": class_name,
                "confidence": round(instance.get("confidence", 0) * 100),
                "timestamp": datetime.now(UTC).isoformat(),
            })

    if results:
        ui.send_message("detections", {"objects": results})


detection.on_detect_all(send_detections)

# Individual callbacks for the three target objects
def on_cup():       print("☕ Cup detected!")
def on_person():    print("🧑 Person detected!")
def on_cell_phone(): print("📱 Cell phone detected!")

detection.on_detect("cup", on_cup)
detection.on_detect("person", on_person)
detection.on_detect("cell phone", on_cell_phone)

print("🤖 AI Vision Recognition running — open the Web UI.")

App.run()
