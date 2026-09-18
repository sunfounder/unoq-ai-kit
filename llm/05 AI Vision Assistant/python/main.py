# SPDX-FileCopyrightText: Copyright (C) SunFounder
#
# SPDX-License-Identifier: MPL-2.0

"""05 AI Vision Assistant

A camera frame is sent to a vision-capable cloud LLM together with your
question. The model describes what it sees or answers about it, and the
answer appears in the Web UI.
"""

import threading
import time

import cv2
from fastapi.responses import StreamingResponse

from arduino.app_bricks.cloud_llm import CloudLLM
from arduino.app_bricks.web_ui import WebUI
from arduino.app_peripherals.camera import Camera
from arduino.app_utils import App, Logger

from sunfounder_tts import EdgeTTS


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TTS_VOICE = "en-US-JennyNeural"

SYSTEM_PROMPT = (
    "You are a friendly visual assistant for students. "
    "Answer only from what is visible in the supplied camera image. "
    "If the answer cannot be determined from the image, say so clearly. "
    "Keep the answer brief, usually one or two sentences. "
    "Reply in the same language as the user's question."
)


# ---------------------------------------------------------------------------
# Services and shared state
# ---------------------------------------------------------------------------

logger = Logger("AIVisionAssistant")
ui = WebUI()

vlm = CloudLLM(
    model="openai:gpt-4o-mini",
    system_prompt=SYSTEM_PROMPT,
    temperature=0.3,
    max_tokens=160,
)
# Each question analyzes only the current frame. Keeping previous image messages
# would make later requests slower and use unnecessary cloud tokens.
vlm.with_memory(max_messages=0)

tts = EdgeTTS()
tts.set_voice(TTS_VOICE)
tts.set_volume(50)

camera = Camera(fps=20)

frame_lock = threading.Lock()
state_lock = threading.Lock()
current_frame = None
busy = False


def send_status(state, message, question="", answer="", room=None):
    """Send the current assistant state to one browser or all browsers."""
    ui.send_message(
        "vision_status",
        {
            "state": state,
            "message": message,
            "question": question,
            "answer": answer,
        },
        room=room,
    )


# ---------------------------------------------------------------------------
# Camera preview
# ---------------------------------------------------------------------------

def generate_frames():
    """Generate an MJPEG stream from the most recent camera frame."""
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
        time.sleep(0.05)


def video_stream():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


def loop():
    """Continuously capture frames for the preview and the VLM."""
    global current_frame

    frame = camera.capture()
    if frame is None:
        return

    # Correct the camera's vertical orientation before the frame is used by
    # either the live preview or the vision model.
    frame = cv2.flip(frame, 0)
    encoded_ok, encoded_frame = cv2.imencode(
        ".jpg",
        frame,
        [cv2.IMWRITE_JPEG_QUALITY, 85],
    )
    if not encoded_ok:
        return

    frame_bytes = encoded_frame.tobytes()
    with frame_lock:
        current_frame = frame_bytes


# ---------------------------------------------------------------------------
# Vision question handling
# ---------------------------------------------------------------------------

def process_question(sid, question, frame):
    """Ask the VLM and speak the answer without blocking the Web UI."""
    global busy
    answer = ""

    try:
        send_status(
            "thinking",
            "AI is looking at the image...",
            question=question,
            room=sid,
        )

        answer = vlm.chat(
            message=question,
            images=[frame],
        ).strip()

        if not answer:
            answer = "Sorry, I could not describe the image. Please try again."

        send_status(
            "speaking",
            "Speaking...",
            question=question,
            answer=answer,
            room=sid,
        )

        tts.say(answer)

        send_status(
            "ready",
            "Ask another question about the camera image.",
            question=question,
            answer=answer,
            room=sid,
        )

    except Exception as error:
        logger.exception(f"Vision assistant failed: {error}")
        send_status(
            "error",
            f"Vision assistant error: {type(error).__name__}: {error}",
            question=question,
            answer=answer,
            room=sid,
        )

    finally:
        with state_lock:
            busy = False


def ask_ai(sid, data):
    """Validate a question and start one vision request."""
    global busy

    question = str((data or {}).get("question", "")).strip()
    if not question:
        send_status(
            "error",
            "Enter a question before asking the AI.",
            room=sid,
        )
        return

    question = question[:300]

    with state_lock:
        if busy:
            send_status(
                "thinking",
                "Please wait for the current answer.",
                question=question,
                room=sid,
            )
            return
        busy = True

    with frame_lock:
        frame = current_frame

    if frame is None:
        with state_lock:
            busy = False
        send_status(
            "error",
            "The camera image is not ready yet. Please try again.",
            question=question,
            room=sid,
        )
        return

    send_status(
        "capturing",
        "Image captured.",
        question=question,
        room=sid,
    )

    threading.Thread(
        target=process_question,
        args=(sid, question, frame),
        daemon=True,
    ).start()


ui.expose_api("GET", "/stream", video_stream)
ui.on_message("ask_ai", ask_ai)

print("AI Vision Assistant ready.")
print("Open App Lab, enter a question, and click ASK AI.")

with camera:
    App.run(user_loop=loop)
