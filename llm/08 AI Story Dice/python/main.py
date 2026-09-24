# SPDX-FileCopyrightText: Copyright (C) SunFounder
#
# SPDX-License-Identifier: MPL-2.0

"""AI Story Dice

Place two or three objects in view, choose a story style, and let a
vision-capable LLM turn the objects into a short story. The Web UI displays
the result, TTS narrates it, and the UNO Q LED matrix shows the story mood.
"""

import json
import re
import threading
import time

import cv2
from fastapi.responses import StreamingResponse

from arduino.app_bricks.cloud_llm import CloudLLM
from arduino.app_bricks.web_ui import WebUI
from arduino.app_peripherals.camera import Camera
from arduino.app_utils import App, Bridge, Logger

from sunfounder_tts import EdgeTTS


TTS_VOICE = "en-US-JennyNeural"

MOOD_CODES = {
    "calm": 0,
    "happy": 1,
    "mysterious": 2,
    "exciting": 3,
}

SYSTEM_PROMPT = (
    "You are a creative storyteller for students. Examine only the supplied "
    "camera image and identify up to three clear, ordinary objects. Never "
    "claim to see an object that is not visible. Use the visible objects as "
    "important parts of an age-friendly story in the requested style. Avoid "
    "violence, fear, adult content, brands, and personal identification. "
    "Return only valid JSON with this exact structure: "
    "{\"objects\":[\"object 1\",\"object 2\"],\"title\":\"Short title\","
    "\"story\":\"Exactly three short sentences\","
    "\"mood\":\"happy\"}. "
    "Allowed moods are happy, mysterious, exciting, and calm. Keep the whole "
    "story under 70 words."
)


logger = Logger("AIStoryDice")
ui = WebUI()

llm = CloudLLM(
    model="openai:gpt-4o-mini",
    system_prompt=SYSTEM_PROMPT,
    temperature=0.8,
    max_tokens=180,
)
llm.with_memory(max_messages=0)

tts = EdgeTTS()
tts.set_voice(TTS_VOICE)
tts.set_volume(50)

camera = Camera(fps=20)

frame_lock = threading.Lock()
state_lock = threading.Lock()
current_frame = None
busy = False
last_result = None


def send_state(state, message, result=None, room=None):
    """Send the current story state to one browser or all browsers."""
    with state_lock:
        saved_result = dict(last_result) if last_result else None

    ui.send_message(
        "story_state",
        {
            "state": state,
            "message": message,
            "result": result if result is not None else saved_result,
        },
        room=room,
    )


def show_mood(mood):
    try:
        Bridge.call("show_story_mood", MOOD_CODES.get(mood, 0))
    except Exception as error:
        logger.warning(f"LED matrix unavailable: {error}")


def speak(text):
    try:
        tts.say(text)
    except Exception as error:
        logger.warning(f"TTS unavailable: {error}")


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
        time.sleep(0.05)


def video_stream():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


def loop():
    global current_frame

    frame = camera.capture()
    if frame is None:
        return

    # Correct the camera orientation before both preview and AI analysis.
    frame = cv2.flip(frame, 0)
    encoded_ok, encoded_frame = cv2.imencode(
        ".jpg",
        frame,
        [cv2.IMWRITE_JPEG_QUALITY, 85],
    )
    if not encoded_ok:
        return

    with frame_lock:
        current_frame = encoded_frame.tobytes()


def parse_story(text):
    """Parse and validate the structured story response."""
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("The AI did not return story JSON.")

    data = json.loads(match.group(0))
    raw_objects = data.get("objects", [])
    if not isinstance(raw_objects, list):
        raw_objects = []

    objects = []
    for item in raw_objects[:3]:
        name = " ".join(str(item).split())[:40]
        if name:
            objects.append(name)

    title = " ".join(str(data.get("title", "")).split())[:80]
    story = " ".join(str(data.get("story", "")).split())[:600]
    mood = str(data.get("mood", "calm")).strip().lower()

    if not objects:
        raise ValueError("No clear objects were found in the image.")
    if not title or not story:
        raise ValueError("The AI returned an incomplete story.")
    if mood not in MOOD_CODES:
        mood = "calm"

    return {
        "objects": objects,
        "title": title,
        "story": story,
        "mood": mood,
    }


def create_story(sid, genre, frame):
    global busy, last_result

    try:
        show_mood("mysterious")
        send_state("thinking", "AI is finding the objects and writing a story...", room=sid)

        prompt = (
            f"Story style: {genre}. "
            "Identify up to three clear objects in the image and create the story now."
        )
        result = parse_story(llm.chat(message=prompt, images=[frame]))

        with state_lock:
            last_result = result

        show_mood(result["mood"])
        send_state("speaking", "The storyteller is reading your story...", result, room=sid)
        speak(f"{result['title']}. {result['story']}")
        send_state("ready", "Change the objects or style to create another story.", result, room=sid)

    except Exception as error:
        logger.exception(f"Story creation failed: {error}")
        show_mood("calm")
        send_state(
            "error",
            f"Unable to create a story: {type(error).__name__}: {error}",
            room=sid,
        )

    finally:
        with state_lock:
            busy = False


def request_story(sid, data):
    global busy

    allowed_genres = {"adventure", "funny", "mystery", "magical", "space"}
    genre = str((data or {}).get("genre", "adventure")).strip().lower()
    if genre not in allowed_genres:
        genre = "adventure"

    with state_lock:
        if busy:
            return
        busy = True

    with frame_lock:
        frame = current_frame

    if frame is None:
        with state_lock:
            busy = False
        send_state("error", "The camera image is not ready yet.", room=sid)
        return

    send_state("capturing", "Camera image captured.", room=sid)
    threading.Thread(
        target=create_story,
        args=(sid, genre, frame),
        daemon=True,
    ).start()


def send_current_state(sid, _data):
    send_state(
        "ready",
        "Place two or three objects in view and create a story.",
        room=sid,
    )


ui.expose_api("GET", "/stream", video_stream)
ui.on_message("get_state", send_current_state)
ui.on_message("create_story", request_story)

print("AI Story Dice ready.")
print("Place two or three objects in view, then open App Launch.")

with camera:
    App.run(user_loop=loop)
