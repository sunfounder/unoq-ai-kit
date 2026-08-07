# SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
#
# SPDX-License-Identifier: MPL-2.0

"""
Camera Preview

The VideoObjectDetection brick is used only to provide the live video
preview service required by App Lab. This example does not process or
display detection results.
"""

from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from arduino.app_peripherals.camera import Camera

# Serve the custom web interface from the assets folder.
ui = WebUI()

# Start the CSI camera and flip the image vertically.
camera = Camera(adjustments=lambda frame: frame[::-1, :])
camera.start()

# Start the video preview service used by the embedded iframe.
# No detection callbacks are registered, so the web page only shows video.
video_stream = VideoObjectDetection(
    camera,
    confidence=0.99,
    debounce_sec=999.0,
)

App.run()
