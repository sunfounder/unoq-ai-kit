# SPDX-FileCopyrightText: Copyright (C) SunFounder
#
# SPDX-License-Identifier: MPL-2.0

"""AI Scavenger Hunt

The AI creates a safe visual challenge. The player shows an object to the
camera and asks the vision-capable LLM to judge it. An RGB LED, a buzzer, the
Web UI, and TTS provide feedback.
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

TASK_SYSTEM_PROMPT = (
    "You create safe indoor scavenger-hunt missions for students. "
    "Each mission must ask the player to show one common, portable object to "
    "a camera. Use a visible property or an everyday purpose, such as color, "
    "shape, material, or use. Never request sharp, hot, heavy, breakable, "
    "dangerous, expensive, private, or living things. Do not request liquids. "
    "Return exactly one short English mission beginning with 'Find'. "
    "Do not add quotes, numbering, hints, or explanations."
)

JUDGE_SYSTEM_PROMPT = (
    "You are the fair referee for a children's visual scavenger hunt. "
    "Judge only what is clearly visible in the supplied camera image. "
    "A result is successful only when the main visible object clearly meets "
    "the mission. If the image is unclear or the requirement cannot be "
    "verified visually, mark it unsuccessful. Return only valid JSON using "
    "this schema: {\"success\": true, \"message\": \"One short sentence\"}. "
    "The message must briefly explain the decision in friendly English."
)


logger = Logger("AIScavengerHunt")
ui = WebUI()

task_llm = CloudLLM(
    model="openai:gpt-4o-mini",
    system_prompt=TASK_SYSTEM_PROMPT,
    temperature=0.9,
    max_tokens=40,
)
task_llm.with_memory(max_messages=0)

judge_llm = CloudLLM(
    model="openai:gpt-4o-mini",
    system_prompt=JUDGE_SYSTEM_PROMPT,
    temperature=0.1,
    max_tokens=100,
)
judge_llm.with_memory(max_messages=0)

tts = EdgeTTS()
tts.set_voice(TTS_VOICE)
tts.set_volume(50)

camera = Camera(fps=20)

frame_lock = threading.Lock()
state_lock = threading.Lock()
current_frame = None
current_task = ""
score = 0
attempts = 0
busy = False
recent_tasks = []


def send_state(state, message, result="", room=None):
    """Send the complete game state to one browser or all browsers."""
    with state_lock:
        payload = {
            "state": state,
            "message": message,
            "task": current_task,
            "score": score,
            "attempts": attempts,
            "result": result,
        }
    ui.send_message("game_state", payload, room=room)


def hardware_feedback(code):
    """Send a feedback code to the Arduino sketch."""
    try:
        Bridge.call("game_feedback", code)
    except Exception as error:
        logger.warning(f"Hardware feedback unavailable: {error}")


def speak(text):
    """Speak when audio is available without breaking the game if it is not."""
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


def clean_task(text):
    """Convert a model response into one short mission sentence."""
    task = text.strip().strip('"').strip("'")
    task = re.sub(r"^\s*[-*\d.)]+\s*", "", task)
    task = " ".join(task.split())
    if not task.lower().startswith("find "):
        task = f"Find {task[0].lower() + task[1:]}" if task else ""
    return task[:140]


def parse_judgement(text):
    """Parse the strict JSON returned by the visual referee."""
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("The AI referee did not return JSON.")
    data = json.loads(match.group(0))
    success = data.get("success") is True
    message = str(data.get("message", "")).strip()
    if not message:
        message = (
            "Great find! That object matches the mission."
            if success
            else "That object does not clearly match the mission yet."
        )
    return success, message[:240]


def create_mission(sid):
    global busy, current_task
    try:
        send_state("generating", "AI is creating a new mission...", room=sid)
        with state_lock:
            avoid = list(recent_tasks[-5:])
        prompt = "Create one new scavenger-hunt mission."
        if avoid:
            prompt += " Do not repeat these recent missions: " + " | ".join(avoid)
        mission = clean_task(task_llm.chat(message=prompt))
        if not mission:
            raise RuntimeError("The AI did not create a mission.")
        with state_lock:
            current_task = mission
            recent_tasks.append(mission)
        hardware_feedback(1)
        send_state("speaking", "Listen to your new mission...", room=sid)
        speak(f"Your mission is: {mission}")
        send_state(
            "ready",
            "Show a matching object to the camera, then check it.",
            room=sid,
        )
    except Exception as error:
        logger.exception(f"Mission generation failed: {error}")
        hardware_feedback(3)
        send_state(
            "error",
            f"Unable to create a mission: {type(error).__name__}: {error}",
            room=sid,
        )
    finally:
        with state_lock:
            busy = False


def request_new_mission(sid, _data):
    global busy
    with state_lock:
        if busy:
            return
        busy = True
    threading.Thread(target=create_mission, args=(sid,), daemon=True).start()


def judge_object(sid, mission, frame):
    global busy, score, attempts
    try:
        hardware_feedback(1)
        send_state("thinking", "AI is checking the camera image...", room=sid)
        prompt = (
            f"Mission: {mission}\n"
            "Judge whether the main object visible in this image completes the mission."
        )
        response = judge_llm.chat(message=prompt, images=[frame])
        success, explanation = parse_judgement(response)
        with state_lock:
            attempts += 1
            if success:
                score += 1
        hardware_feedback(2 if success else 3)
        send_state(
            "success" if success else "try_again",
            "Mission complete!" if success else "Not quite. Try again!",
            result=explanation,
            room=sid,
        )
        speech = (
            f"Mission complete! {explanation}"
            if success
            else f"Not quite. {explanation} Try again."
        )
        speak(speech)
        send_state(
            "complete" if success else "ready",
            (
                "Choose NEW MISSION to continue."
                if success
                else "Show another object and check again."
            ),
            result=explanation,
            room=sid,
        )
    except Exception as error:
        logger.exception(f"Object check failed: {error}")
        hardware_feedback(3)
        send_state(
            "error",
            f"Unable to check the object: {type(error).__name__}: {error}",
            room=sid,
        )
    finally:
        with state_lock:
            busy = False


def check_object(sid, _data):
    global busy
    with state_lock:
        if busy:
            return
        mission = current_task
        if mission:
            busy = True
    if not mission:
        send_state("error", "Choose NEW MISSION first.", room=sid)
        return
    with frame_lock:
        frame = current_frame
    if frame is None:
        with state_lock:
            busy = False
        send_state("error", "The camera image is not ready yet.", room=sid)
        return
    send_state("capturing", "Camera image captured.", room=sid)
    threading.Thread(
        target=judge_object,
        args=(sid, mission, frame),
        daemon=True,
    ).start()


def send_current_state(sid, _data):
    send_state(
        "ready",
        (
            "Show a matching object to the camera, then check it."
            if current_task
            else "Choose NEW MISSION to begin."
        ),
        room=sid,
    )


def reset_game(sid, _data):
    global score, attempts, current_task
    with state_lock:
        if busy:
            return
        score = 0
        attempts = 0
        current_task = ""
    hardware_feedback(0)
    send_state("ready", "Score reset. Choose NEW MISSION to begin.", room=sid)


ui.expose_api("GET", "/stream", video_stream)
ui.on_message("get_state", send_current_state)
ui.on_message("new_mission", request_new_mission)
ui.on_message("check_object", check_object)
ui.on_message("reset_game", reset_game)

print("AI Scavenger Hunt ready.")
print("Open App Launch and choose NEW MISSION to begin.")

with camera:
    App.run(user_loop=loop)
