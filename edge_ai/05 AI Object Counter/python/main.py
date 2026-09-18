# SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
# SPDX-License-Identifier: MPL-2.0

"""AI Object Counter.

Detect mice, keyboards, and cell phones and count each new appearance once.
An object must leave the camera view before the same class can be counted again.
Each new count is also announced through online text-to-speech.
"""

import queue
import threading

from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from arduino.app_peripherals.camera import Camera
from sunfounder_tts import EdgeTTS


TARGETS = ("mouse", "keyboard", "cell phone")
CONFIDENCE_THRESHOLD = 0.60
MISSING_FRAMES_TO_REARM = 10
TTS_VOICE = "en-US-JennyNeural"
TTS_VOLUME = 50

SPEECH_TEXT = {
    "mouse": "Mouse detected",
    "keyboard": "Keyboard detected",
    "cell phone": "Cell phone detected",
}

ui = WebUI()

camera = Camera(adjustments=lambda frame: frame[::-1, :])
camera.start()

detection = VideoObjectDetection(
    camera,
    confidence=CONFIDENCE_THRESHOLD,
    debounce_sec=0.2,
)

state_lock = threading.Lock()
counts = {label: 0 for label in TARGETS}
armed = {label: True for label in TARGETS}
missing_frames = {label: 0 for label in TARGETS}
last_detection = None
speech_queue = queue.Queue()


def speech_worker():
    """Play queued messages without blocking object detection."""
    try:
        tts = EdgeTTS()
        tts.set_voice(TTS_VOICE)
        tts.set_volume(TTS_VOLUME)
        print("TTS ready.", flush=True)

        while True:
            text = speech_queue.get()

            try:
                tts.say(text)
            except Exception as error:
                print(
                    f"TTS error: {type(error).__name__}: {error}",
                    flush=True,
                )
            finally:
                speech_queue.task_done()

    except Exception as error:
        print(
            f"TTS startup failed: {type(error).__name__}: {error}",
            flush=True,
        )


def speak(label):
    """Queue the spoken name for a newly counted object."""
    speech_queue.put(SPEECH_TEXT[label])


def public_state():
    """Return the counter state for the Web UI."""
    with state_lock:
        return {
            "counts": dict(counts),
            "total": sum(counts.values()),
            "last_detection": (
                dict(last_detection) if last_detection else None
            ),
        }


def publish_state():
    ui.send_message("counter_state", public_state())


def reset_counts():
    """Reset all counters without changing the current detection locks."""
    global last_detection

    with state_lock:
        for label in TARGETS:
            counts[label] = 0
        last_detection = None

    publish_state()
    return public_state()


ui.expose_api("GET", "/state", public_state)
ui.expose_api("POST", "/reset-counts", reset_counts)


def on_detection(detections: dict):
    """Count a target once, then wait until it leaves before rearming."""
    global last_detection

    counted_items = []

    with state_lock:
        for label in TARGETS:
            instances = detections.get(label, [])
            best_confidence = max(
                (
                    instance.get("confidence", 0)
                    for instance in instances
                ),
                default=0,
            )
            present = best_confidence >= CONFIDENCE_THRESHOLD

            if present:
                missing_frames[label] = 0

                if armed[label]:
                    counts[label] += 1
                    armed[label] = False
                    counted_items.append((label, best_confidence))
            elif not armed[label]:
                missing_frames[label] += 1

                if missing_frames[label] >= MISSING_FRAMES_TO_REARM:
                    armed[label] = True
                    missing_frames[label] = 0

        if counted_items:
            counted_label, counted_confidence = counted_items[-1]
            last_detection = {
                "object": counted_label,
                "confidence": round(counted_confidence * 100),
            }

    if counted_items:
        for counted_label, counted_confidence in counted_items:
            speak(counted_label)
            print(
                f"Counted {counted_label}: "
                f"{counts[counted_label]} "
                f"({counted_confidence:.0%})",
                flush=True,
            )

        publish_state()


detection.on_detect_all(on_detection)

threading.Thread(target=speech_worker, daemon=True).start()

print(
    "AI Object Counter is running. "
    "Show one mouse, keyboard, or cell phone at a time.",
    flush=True,
)

App.run()
