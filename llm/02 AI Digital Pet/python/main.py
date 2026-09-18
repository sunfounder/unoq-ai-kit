# SPDX-FileCopyrightText: Copyright (C) SunFounder
#
# SPDX-License-Identifier: MPL-2.0

"""02 AI Digital Pet

A cloud LLM plays a small pet whose mood is drawn on the LED matrix.
The Web UI sends a message, the model answers with words and a mood,
and the sketch animates the matching expression on the LED matrix.
"""

import json
import re

from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.cloud_llm import CloudLLM

ui = WebUI()

EMOTION_CODES = {
    "neutral": 0,
    "happy": 1,
    "sad": 2,
    "surprised": 3,
    "thinking": 4,
}

SYSTEM_PROMPT = """You are Pixel, a friendly AI digital pet.

Reply to the user's message in one short, friendly sentence.
Choose the emotion that best matches your reply.

Available emotions:
happy
sad
surprised
thinking
neutral

Return ONLY valid JSON in this exact format:
{"emotion":"happy","reply":"Your short reply here."}

Do not use Markdown or code fences. Do not add any text outside the JSON."""

llm = CloudLLM(
    model="openai:gpt-4o-mini",
    system_prompt=SYSTEM_PROMPT,
)


def parse_pet_response(raw_response):
    """Parse the model JSON and safely fall back to a neutral expression."""
    cleaned = raw_response.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if match:
        cleaned = match.group(0)

    try:
        result = json.loads(cleaned)
    except (json.JSONDecodeError, TypeError):
        return "neutral", "I am here with you."

    emotion = str(result.get("emotion", "neutral")).strip().lower()
    if emotion not in EMOTION_CODES:
        emotion = "neutral"

    reply = str(result.get("reply", "")).strip()
    if not reply:
        reply = "I am here with you."

    return emotion, reply[:240]


def handle_message(client, data):
    text = (data.get("text") or "").strip()
    if not text:
        return

    # Show that the pet is processing the message.
    Bridge.call("show_emotion", EMOTION_CODES["thinking"])
    ui.send_message("pet_status", {"emotion": "thinking"})

    try:
        raw_response = "".join(llm.chat_stream(message=text))
        emotion, reply = parse_pet_response(raw_response)
    except Exception as error:
        print(f"[LLM ERROR] {type(error).__name__}: {error}", flush=True)
        Bridge.call("show_emotion", EMOTION_CODES["neutral"])
        ui.send_message("response", {
            "emotion": "neutral",
            "reply": "Please configure your API Key and try again.",
        })
        return

    Bridge.call("show_emotion", EMOTION_CODES[emotion])

    print(f"[PET] emotion={emotion} reply={reply}", flush=True)
    ui.send_message("response", {
        "emotion": emotion,
        "reply": reply,
    })


ui.on_message("message", handle_message)

print("AI Digital Pet ready — configure your API Key and start chatting!", flush=True)

App.run()
