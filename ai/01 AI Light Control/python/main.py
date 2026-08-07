# SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
#
# SPDX-License-Identifier: MPL-2.0

"""
AI Light Control

Talk to an RGB LED — the AI understands your words and
controls the hardware. Speak naturally, the AI handles the rest.
"""

from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.cloud_llm import CloudLLM

ui = WebUI()

COLORS = ["red", "green", "blue", "yellow", "white"]

# Color name → code (matches sketch.ino switch cases)
COLOR_CODES = {
    "red":    1,
    "green":  2,
    "blue":   3,
    "yellow": 4,
    "white":  5,
    "off":    0,
}

SYSTEM_PROMPT = (
    "You are an AI assistant controlling an RGB LED.\n\n"
    "Supported colors:\n"
    + "\n".join(COLORS)
    + "\n\n"
    "If the user wants to turn off the light, reply with:\n\n"
    "off\n\n"
    "Reply with ONLY ONE WORD."
)

llm = CloudLLM(
    model="openai:gpt-4o-mini",
    system_prompt=SYSTEM_PROMPT,
)


def handle_command(client, data):
    text = (data.get("text") or "").strip()
    if not text:
        return

    try:
        response = "".join(llm.chat_stream(message=text))
        color = response.strip().lower()
    except Exception:
        ui.send_message("response", {
            "text": "Please configure your API Key.",
            "color": None,
        })
        return

    if color in COLOR_CODES:
        code = COLOR_CODES[color]
        Bridge.call("set_color", code)

        ui.send_message("response", {
            "text": "Light turned off" if color == "off" else f"Light set to {color}",
            "color": color,
        })
    else:
        ui.send_message("response", {
            "text": f"I don't know that color. Try: {', '.join(COLORS)} or off.",
            "color": None,
        })


ui.on_message("command", handle_command)

print("💬 AI Light Control ready — configure your API Key and start chatting!")

App.run()
