# SPDX-FileCopyrightText: Copyright (C) SunFounder
#
# SPDX-License-Identifier: MPL-2.0

"""
AI Voice Vision Assistant V7

This project keeps the working Voice Assistant audio flow and combines it
with the working Camera Basics live-stream method.

Voice:
    RobotShield microphone -> local Whisper STT -> CloudLLM -> EdgeTTS

Vision:
    CSI camera -> VideoObjectDetection preview service -> Web UI iframe
    Visual question -> capture current frame -> CloudLLM Vision

Hardware:
    Voice command -> Bridge -> external LED on D5
"""

import json
import os
import re
import threading

from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.cloud_llm import CloudLLM
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from arduino.app_peripherals.camera import Camera
from arduino.app_utils.image.adjustments import compress_to_jpeg

from sunfounder_stt import STT
from sunfounder_tts import EdgeTTS


# ---------------------------------------------------------------------------
# Configuration copied from the working Voice Assistant example
# ---------------------------------------------------------------------------

STT_LANGUAGE = "en"

TTS_VOICE = "en-US-JennyNeural"

VISION_PHRASES = (
    "what do you see",
    "what can you see",
    "what are you seeing",
    "describe what you see",
    "describe the scene",
    "look at the camera",
    "look in front of you",
    "can you see",
    "what is in front of you",
    "你看到了什么",
    "你能看到什么",
    "描述一下画面",
    "看看前面",
    "摄像头里有什么",
)

SYSTEM_PROMPT = (
    "You are a friendly voice assistant connected to a camera and one LED. "
    "Always reply in the same language as the user. "
    "Reply naturally and briefly, usually in one or two sentences. "
    "Return ONLY valid JSON in this exact format: "
    '{"reply":"your answer","led":"on|off|none"}. '
    "Use led=on when the user asks to turn on or light the LED. "
    "Use led=off when the user asks to turn off the LED. "
    "Otherwise use led=none. "
    "When an image is provided, describe only what is visible in the image. "
    "Do not wrap the JSON in Markdown."
)


# ---------------------------------------------------------------------------
# Audio and AI services
# ---------------------------------------------------------------------------

os.makedirs("/app/audio_output", exist_ok=True)
os.makedirs("./audio_output", exist_ok=True)

ui = WebUI()

stt = STT(
    type="local_fast",
    language=STT_LANGUAGE,
)

llm = CloudLLM(
    model="openai:gpt-4o-mini",
    system_prompt=SYSTEM_PROMPT,
)

tts = EdgeTTS()
tts.set_voice(TTS_VOICE)
tts.set_volume(50)


# ---------------------------------------------------------------------------
# Camera and live preview service copied from Camera Basics
# ---------------------------------------------------------------------------

camera = Camera(adjustments=lambda frame: frame[::-1, :])
camera.start()

# This brick provides the smooth live stream at http://BOARD_IP:4912/embed.
# No detection callbacks are registered; it is used only as a preview service.
video_stream = VideoObjectDetection(
    camera,
    confidence=0.99,
    debounce_sec=999.0,
)

camera_lock = threading.Lock()


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

state_lock = threading.Lock()
recording = False
busy = False
led_is_on = False


def send_status(state, message, heard="", reply=""):
    """Send the current assistant state to the browser."""
    ui.send_message(
        "voice_status",
        {
            "state": state,
            "message": message,
            "heard": heard,
            "reply": reply,
            "led_on": led_is_on,
        },
    )


def is_vision_question(text):
    lowered = text.lower()
    return any(phrase in lowered for phrase in VISION_PHRASES)


def capture_current_image():
    """Capture the newest camera frame and return JPEG bytes for CloudLLM."""
    with camera_lock:
        frame = camera.capture()

    if frame is None:
        return None

    jpeg = compress_to_jpeg(frame)
    if jpeg is None:
        return None

    return jpeg.tobytes()


def parse_llm_json(raw_text):
    """Parse the JSON response and tolerate accidental surrounding text."""
    text = (raw_text or "").strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        data = json.loads(match.group(0))

    if not isinstance(data, dict):
        raise ValueError("LLM response was not a JSON object")

    return data


def apply_led_command(command):
    global led_is_on

    if command == "on":
        led_is_on = True
        Bridge.call("set_led", 1)
    elif command == "off":
        led_is_on = False
        Bridge.call("set_led", 0)
    else:
        return

    ui.send_message("led_status", {"on": led_is_on})


def start_recording(client, data):
    """Begin recording when the web button is pressed."""
    global recording

    with state_lock:
        if recording or busy:
            return
        recording = True

    try:
        stt.reset()
        stt.start_listening()

        send_status(
            "listening",
            "Listening... Release the button when you finish speaking.",
        )

    except Exception as error:
        with state_lock:
            recording = False

        send_status(
            "error",
            f"Unable to start recording: {type(error).__name__}: {error}",
        )


def process_voice():
    """Stop recording, transcribe, ask the LLM, and speak its reply."""
    global busy

    heard = ""
    reply = ""

    try:
        stt.stop_listening()
        send_status("recognizing", "Recognizing your speech...")

        result = stt.get_result(timeout=60)
        if isinstance(result, dict):
            result = result.get("text", "")
        heard = result.strip() if result else ""

        if not heard:
            send_status(
                "ready",
                "No speech was recognized. Hold the button and try again.",
            )
            return

        images = None

        if is_vision_question(heard):
            send_status(
                "looking",
                "Looking at the current camera view...",
                heard=heard,
            )
            image_bytes = capture_current_image()
            if image_bytes:
                images = [image_bytes]

        send_status(
            "thinking",
            "AI is thinking...",
            heard=heard,
        )

        raw_reply = "".join(
            llm.chat_stream(
                message=heard,
                images=images,
            )
        ).strip()

        result = parse_llm_json(raw_reply)
        reply = str(result.get("reply") or "").strip()
        led_command = str(result.get("led") or "none").strip().lower()

        apply_led_command(led_command)

        if not reply:
            reply = "Sorry, I could not generate a response."

        send_status(
            "speaking",
            "Speaking...",
            heard=heard,
            reply=reply,
        )

        tts.say(reply)

        send_status(
            "ready",
            "Hold the button and speak.",
            heard=heard,
            reply=reply,
        )

    except Exception as error:
        send_status(
            "error",
            f"Voice assistant error: {type(error).__name__}: {error}",
            heard=heard,
            reply=reply,
        )

    finally:
        with state_lock:
            busy = False


def stop_recording(client, data):
    """Finish recording when the web button is released."""
    global recording, busy

    with state_lock:
        if not recording or busy:
            return

        recording = False
        busy = True

    threading.Thread(
        target=process_voice,
        daemon=True,
    ).start()


ui.on_message("start_recording", start_recording)
ui.on_message("stop_recording", stop_recording)

print("AI Voice Vision Assistant V7 ready.")
App.run()
