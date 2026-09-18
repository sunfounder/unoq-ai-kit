# SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
#
# SPDX-License-Identifier: MPL-2.0

"""
AI Vision Recognition — detect common objects in the camera feed.

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

# Video object detection — general model for common objects
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

print("🤖 AI Vision Recognition running — open the Web UI.")

App.run()
