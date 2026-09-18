# SPDX-FileCopyrightText: Copyright (C) SunFounder
#
# SPDX-License-Identifier: MPL-2.0

"""
AI Voice Assistant

Hold the button in the Web UI and speak.

    RobotShield microphone
            ↓
    sunfounder_stt
            ↓
       CloudLLM
            ↓
    sunfounder_tts
            ↓
    RobotShield speaker

The physical USR button is not used.
"""

import os
import threading

from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.cloud_llm import CloudLLM

from sunfounder_stt import STT
from sunfounder_tts import EdgeTTS


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

STT_LANGUAGE = "en"

TTS_VOICE = "en-US-JennyNeural"

SYSTEM_PROMPT = (
    "You are a friendly voice assistant. "
    "Answer naturally and briefly, usually in one or two sentences. "
    "Always reply in the same language as the user."
)


# ---------------------------------------------------------------------------
# Audio and AI services
# ---------------------------------------------------------------------------

# Both sunfounder_stt and sunfounder_tts save temporary audio files here.
os.makedirs("/app/audio_output", exist_ok=True)
os.makedirs("./audio_output", exist_ok=True)

ui = WebUI()

# Local Whisper STT does not consume the CloudLLM API key.
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
# State
# ---------------------------------------------------------------------------

state_lock = threading.Lock()
recording = False
busy = False


def send_status(state, message, heard="", reply=""):
    """Send the current assistant state to the browser."""
    ui.send_message(
        "voice_status",
        {
            "state": state,
            "message": message,
            "heard": heard,
            "reply": reply,
        },
    )


def start_recording(client, data):
    """Begin recording when the web button is pressed."""
    global recording

    with state_lock:
        if recording or busy:
            return
        recording = True

    try:
        # Clear any stale state before starting a new recording.
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

        send_status(
            "thinking",
            "AI is thinking...",
            heard=heard,
        )

        reply = "".join(
            llm.chat_stream(message=heard)
        ).strip()

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

    # STT, LLM, and TTS may take time, so keep the WebUI callback responsive.
    threading.Thread(
        target=process_voice,
        daemon=True,
    ).start()


ui.on_message("start_recording", start_recording)
ui.on_message("stop_recording", stop_recording)

print("AI Voice Assistant ready.")
App.run()
