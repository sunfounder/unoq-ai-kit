# SPDX-FileCopyrightText: Copyright (C) SunFounder
#
# SPDX-License-Identifier: MPL-2.0

"""09 AI Show and Tell

Hold the Web UI button and ask a question about an object in the camera view.
Online GPT STT transcribes the speech, a vision-capable LLM answers from the
captured image, and TTS reads the answer aloud.
"""

import os
import threading
import time

import cv2
from fastapi.responses import StreamingResponse

from arduino.app_bricks.cloud_llm import CloudLLM
from arduino.app_bricks.web_ui import WebUI
from arduino.app_peripherals.camera import Camera
from arduino.app_utils import App, Logger

from sunfounder_stt import STT
from sunfounder_tts import EdgeTTS

try:
    from robot_shield import setup_audio_output
except ImportError:
    setup_audio_output = None


STT_LANGUAGE = "en"
TTS_VOICE = "en-US-JennyNeural"
MAX_QUESTION_LENGTH = 300

SYSTEM_PROMPT = (
    "You are a friendly show-and-tell assistant for students. "
    "Answer the spoken question using only what is visible in the supplied "
    "camera image. If the requested detail cannot be determined from the "
    "image, say so clearly. Do not identify a person or infer sensitive "
    "personal information. Keep the answer age-friendly and concise, usually "
    "one or two sentences. Reply in the same language as the question."
)


logger = Logger("AIShowAndTell")
ui = WebUI()

if setup_audio_output is not None:
    try:
        setup_audio_output()
    except Exception as error:
        logger.warning(f"Audio mixer setup unavailable: {error}")

stt = STT(type="online", language=STT_LANGUAGE)
stt_key = (
    os.environ.get("OPENAI_API_KEY", "").strip()
    or os.environ.get("API_KEY", "").strip()
)
if stt_key:
    STT.API_KEY = stt_key

llm = CloudLLM(
    model="openai:gpt-4o-mini",
    system_prompt=SYSTEM_PROMPT,
    temperature=0.3,
    max_tokens=160,
)
llm.with_memory(max_messages=0)

tts = EdgeTTS()
tts.set_voice(TTS_VOICE)
tts.set_volume(50)

camera = Camera(fps=10)

frame_lock = threading.Lock()
state_lock = threading.Lock()
current_frame = None
recording = False
busy = False
recording_started_at = 0.0
last_question = ""
last_answer = ""


def send_status(state, message, question="", answer="", room=None):
    ui.send_message(
        "show_tell_status",
        {
            "state": state,
            "message": message,
            "question": question,
            "answer": answer,
        },
        room=room,
    )


def generate_frames():
    while True:
        with frame_lock:
            frame = current_frame

        if frame is None:
            time.sleep(0.1)
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame
            + b"\r\n"
        )
        # Match the camera capture rate and avoid sending duplicate frames too
        # quickly when the browser connection is slower than the camera.
        time.sleep(0.1)


def video_stream():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


def camera_loop():
    """Capture preview frames independently from App and Bridge callbacks."""
    global current_frame

    while True:
        try:
            frame = camera.capture()
            if frame is None:
                time.sleep(0.05)
                continue

            # Correct the camera orientation for both preview and AI analysis.
            frame = cv2.flip(frame, 0)
            encoded_ok, encoded_frame = cv2.imencode(
                ".jpg",
                frame,
                [cv2.IMWRITE_JPEG_QUALITY, 75],
            )
            if encoded_ok:
                with frame_lock:
                    current_frame = encoded_frame.tobytes()

        except Exception as error:
            logger.warning(f"Camera frame unavailable: {error}")
            time.sleep(0.25)

        time.sleep(0.08)


def extract_stt_text(result):
    """Normalize the STT Bridge response into plain text."""
    if isinstance(result, dict):
        result = result.get("text", "")
    return str(result or "").strip()


def start_recording(sid, _data):
    global recording, recording_started_at

    with state_lock:
        if recording or busy:
            return
        recording = True
        recording_started_at = time.monotonic()

    try:
        stt.reset()
        stt.start_listening()
        send_status(
            "listening",
            "Listening... Keep holding the button while you speak.",
            room=sid,
        )

    except Exception as error:
        with state_lock:
            recording = False
        logger.exception(f"Unable to start recording: {error}")
        send_status(
            "error",
            f"Unable to start recording: {type(error).__name__}: {error}",
            room=sid,
        )


def process_question(sid, frame):
    global busy, last_question, last_answer

    question = ""
    answer = ""

    try:
        stt.stop_listening()
        send_status("recognizing", "Converting your speech to text...", room=sid)

        if not STT.API_KEY:
            raise RuntimeError(
                "OpenAI STT API key is missing. Add it in Brick Configuration."
            )

        question = extract_stt_text(stt.get_result(timeout=45))
        if question.startswith("[STT ERROR]"):
            raise RuntimeError(question)

        if not question:
            send_status(
                "ready",
                "No speech was recognized. Hold the button and try again.",
                room=sid,
            )
            return

        question = question[:MAX_QUESTION_LENGTH]
        send_status(
            "thinking",
            "AI is examining the captured image...",
            question=question,
            room=sid,
        )

        answer = llm.chat(message=question, images=[frame]).strip()
        if not answer:
            answer = "Sorry, I could not answer from this image. Please try again."

        with state_lock:
            last_question = question
            last_answer = answer

        send_status(
            "speaking",
            "Reading the answer aloud...",
            question=question,
            answer=answer,
            room=sid,
        )
        tts.say(answer)

        send_status(
            "ready",
            "Hold the button to ask another question.",
            question=question,
            answer=answer,
            room=sid,
        )

    except Exception as error:
        logger.exception(f"Show and tell request failed: {error}")
        send_status(
            "error",
            f"Unable to answer: {type(error).__name__}: {error}",
            question=question,
            answer=answer,
            room=sid,
        )

    finally:
        with state_lock:
            busy = False


def stop_recording(sid, _data):
    global recording, busy

    with state_lock:
        if not recording or busy:
            return
        elapsed = time.monotonic() - recording_started_at
        recording = False
        busy = True

    if elapsed < 0.35:
        try:
            stt.stop_listening()
        except Exception:
            pass
        with state_lock:
            busy = False
        send_status(
            "ready",
            "Hold the button while speaking, then release it.",
            room=sid,
        )
        return

    with frame_lock:
        frame = current_frame

    if frame is None:
        try:
            stt.stop_listening()
        except Exception:
            pass
        with state_lock:
            busy = False
        send_status("error", "The camera image is not ready yet.", room=sid)
        return

    send_status("capturing", "Question and camera image captured.", room=sid)
    threading.Thread(
        target=process_question,
        args=(sid, frame),
        daemon=True,
    ).start()


def send_current_state(sid, _data):
    with state_lock:
        question = last_question
        answer = last_answer
        is_busy = busy or recording

    if is_busy:
        send_status(
            "ready",
            "The app is busy. Please wait a moment.",
            question=question,
            answer=answer,
            room=sid,
        )
    else:
        send_status(
            "ready",
            "Hold the button, ask about the object, then release.",
            question=question,
            answer=answer,
            room=sid,
        )


ui.expose_api("GET", "/stream", video_stream)
ui.on_message("get_state", send_current_state)
ui.on_message("start_recording", start_recording)
ui.on_message("stop_recording", stop_recording)

print("AI Show and Tell ready.")
print("Open App Launch, hold the button, and ask about an object.")

with camera:
    threading.Thread(target=camera_loop, daemon=True).start()
    App.run()
