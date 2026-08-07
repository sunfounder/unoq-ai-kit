# SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
#
# SPDX-License-Identifier: MPL-2.0

"""
Face Tracking Camera with Online TTS

The pan servo scans from side to side. When a face is detected,
Python tells the sketch to stop scanning and plays a short greeting.
When the face disappears for 2.5 seconds, scanning resumes automatically.

The greeting uses EdgeTTS:
- Internet access is required.
- No API key is required.
- No STT or LLM service is used.
"""

from datetime import UTC, datetime
import os
import queue
import threading
import time

from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from arduino.app_peripherals.camera import Camera
from robot_shield import setup_audio_output
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
    debounce_sec=0.5,
)

# Face tracking state
face_visible = False
last_face_time = 0.0
face_lock = threading.Lock()
FACE_LOST_TIMEOUT = 2.5

# Greeting configuration
GREETING_TEXT = "Hello, nice to meet you."
GREETING_VOICE = "en-US-JennyNeural"
GREETING_GAIN = 0.40

# TTS runs in a background worker so face detection remains responsive
speech_queue = queue.Queue()


def speech_worker():
    """Play queued messages through EdgeTTS."""
    try:
        # EdgeTTS writes the generated MP3 to ./audio_output.
        # Create the directory before calling tts.say().
        os.makedirs("./audio_output", exist_ok=True)
        os.makedirs("/app/audio_output", exist_ok=True)

        setup_audio_output()

        tts = EdgeTTS(gain=GREETING_GAIN)
        tts.set_voice(GREETING_VOICE)

        print("🔊 EdgeTTS ready — Internet required, no API key needed.")

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


def face_detected():
    """Stop scanning and greet when a new face appears."""
    global face_visible, last_face_time

    is_new_face = False

    with face_lock:
        last_face_time = time.monotonic()

        if not face_visible:
            face_visible = True
            is_new_face = True

    if not is_new_face:
        return

    Bridge.call("stop_scanning")
    speak(GREETING_TEXT)

    ui.send_message("face_status", {
        "detected": True,
        "text": "Face detected — scanning stopped",
        "timestamp": datetime.now(UTC).isoformat(),
    })


def monitor_face_status():
    """Resume scanning when the face has been lost."""
    global face_visible

    while True:
        should_resume = False

        with face_lock:
            if face_visible:
                elapsed = time.monotonic() - last_face_time

                if elapsed >= FACE_LOST_TIMEOUT:
                    face_visible = False
                    should_resume = True

        if should_resume:
            Bridge.call("start_scanning")

            ui.send_message("face_status", {
                "detected": False,
                "text": "Scanning for a face",
                "timestamp": datetime.now(UTC).isoformat(),
            })

        time.sleep(0.2)


detection.on_detect("face", face_detected)

threading.Thread(target=speech_worker, daemon=True).start()
threading.Thread(target=monitor_face_status, daemon=True).start()

print("🤖 Face Tracking Camera with TTS is running.")

App.run()
