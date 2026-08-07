# SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
#
# SPDX-License-Identifier: MPL-2.0

"""
AI Smart Guard

A complete security system:
  - Servo scans left/right (green LED = all clear)
  - Person detected → red LED, buzzer alarm, servo tracks,
    TTS announces "Intruder detected"
  - Person lost for 3 seconds → returns to green/scanning
"""

import os
import queue
import threading
import time
from datetime import datetime, UTC

from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from arduino.app_peripherals.camera import Camera
from robot_shield import setup_audio_output
from sunfounder_tts import EdgeTTS

# ---- Web UI ----
ui = WebUI()

# ---- Camera + Detection ----
camera = Camera(adjustments=lambda frame: frame[::-1, :])
camera.start()

detection = VideoObjectDetection(
    camera,
    confidence=0.4,
    debounce_sec=0.5,
)

# ---- State ----
intruder_visible = False
last_intruder_time = 0.0
state_lock = threading.Lock()
LOST_TIMEOUT = 5.0  # seconds before all-clear
last_spoke_alert = 0.0     # prevent TTS spam

# ---- Voice ----
ALERT_TEXT = "Intruder detected. Intruder detected."
CLEAR_TEXT = "All clear."
speech_queue = queue.Queue()


def speech_worker():
    """Background TTS worker."""
    try:
        os.makedirs("./audio_output", exist_ok=True)
        os.makedirs("/app/audio_output", exist_ok=True)
        setup_audio_output()

        tts = EdgeTTS(gain=0.40)
        tts.set_voice("en-US-JennyNeural")

        print("🔊 TTS ready.")

        while True:
            text = speech_queue.get()
            try:
                tts.say(text)
            except Exception as e:
                print(f"TTS error: {e}")
            finally:
                speech_queue.task_done()
    except Exception as e:
        print(f"TTS init failed: {e}")


def speak(text):
    if text:
        speech_queue.put(str(text))


# ---- Detection callback ----

def person_detected():
    """Called each time the model detects a person."""
    global intruder_visible, last_intruder_time, last_spoke_alert

    now = time.monotonic()

    with state_lock:
        last_intruder_time = now

        if not intruder_visible:
            intruder_visible = True
            Bridge.call("alarm_on")

    # Only speak once every 8 seconds to avoid spamming
    if now - last_spoke_alert > 8.0:
        last_spoke_alert = now
        speak(ALERT_TEXT)

    ui.send_message("guard_status", {
        "alert": True,
        "confidence": 100,
        "message": "🚨 Intruder detected!",
        "timestamp": datetime.now(UTC).isoformat(),
    })


def monitor_guard():
    """Background: return to all-clear after timeout."""
    global intruder_visible

    while True:
        should_clear = False

        with state_lock:
            if intruder_visible:
                if time.monotonic() - last_intruder_time >= LOST_TIMEOUT:
                    intruder_visible = False
                    should_clear = True

        if should_clear:
            Bridge.call("alarm_off")
            speak(CLEAR_TEXT)

            ui.send_message("guard_status", {
                "alert": False,
                "confidence": 0,
                "message": "✅ All clear — scanning",
                "timestamp": datetime.now(UTC).isoformat(),
            })

        time.sleep(0.2)


# ---- Start ----

detection.on_detect("person", person_detected)

threading.Thread(target=speech_worker, daemon=True).start()
threading.Thread(target=monitor_guard, daemon=True).start()

print("🛡️  AI Smart Guard is running.")

App.run()
