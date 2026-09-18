# SPDX-FileCopyrightText: Copyright (C) SunFounder
#
# SPDX-License-Identifier: MPL-2.0

"""03 AI Environment Advisor

Temperature, humidity, and light level are read by the sketch and sent
to a cloud LLM for advice. The Web UI shows the readings, the model's
analysis, and the recommended action.
"""

import json
import re

from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.cloud_llm import CloudLLM

ui = WebUI()

latest_environment = {
    "temperature": None,
    "humidity": None,
    "light_raw": None,
    "light_percent": None,
    "light_label": "Waiting",
}

SYSTEM_PROMPT = """You are an AI environment advisor for a classroom project.

Analyze the temperature, humidity, and relative light level supplied by the user.
Give a simple, practical assessment. Do not claim medical certainty.

Choose exactly one status from:
Comfortable
Warm
Cold
Humid
Dry
Dark
Bright
Mixed

Return ONLY valid JSON in this exact format:
{"status":"Comfortable","summary":"One short sentence.","suggestion":"One short practical suggestion."}

Do not use Markdown or code fences. Do not add text outside the JSON."""

llm = CloudLLM(
    model="openai:gpt-4o-mini",
    system_prompt=SYSTEM_PROMPT,
)

VALID_STATUSES = {
    "comfortable", "warm", "cold", "humid",
    "dry", "dark", "bright", "mixed",
}


def light_description(percent):
    if percent < 25:
        return "Dark"
    if percent < 55:
        return "Dim"
    if percent < 80:
        return "Bright"
    return "Very Bright"


def send_sensor_state():
    ui.send_message("sensor_update", latest_environment)


def environment_update(temperature, humidity, light_raw):
    raw = max(0, min(1023, int(light_raw)))
    percent = round(raw * 100 / 1023)

    latest_environment.update({
        "temperature": round(float(temperature), 1),
        "humidity": round(float(humidity), 1),
        "light_raw": raw,
        "light_percent": percent,
        "light_label": light_description(percent),
    })

    print(
        f"[SENSORS] {latest_environment['temperature']:.1f} C, "
        f"{latest_environment['humidity']:.1f}% RH, "
        f"light {percent}% ({latest_environment['light_label']})",
        flush=True,
    )
    send_sensor_state()


def sensor_error(message):
    print(f"[SENSOR ERROR] {message}", flush=True)
    ui.send_message("sensor_error", {"message": str(message)})


Bridge.provide("environment_update", environment_update)
Bridge.provide("sensor_error", sensor_error)


def parse_analysis(raw_response):
    cleaned = raw_response.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if match:
        cleaned = match.group(0)

    try:
        result = json.loads(cleaned)
    except (json.JSONDecodeError, TypeError):
        return {
            "status": "Mixed",
            "summary": "The AI response could not be read safely.",
            "suggestion": "Please try the analysis again.",
        }

    status = str(result.get("status", "Mixed")).strip().lower()
    if status not in VALID_STATUSES:
        status = "mixed"

    summary = str(result.get("summary", "")).strip()
    suggestion = str(result.get("suggestion", "")).strip()

    return {
        "status": status.title(),
        "summary": (summary or "The environment has been analyzed.")[:240],
        "suggestion": (suggestion or "Keep monitoring the sensor readings.")[:240],
    }


def request_state(client, data):
    send_sensor_state()


def analyze_environment(client, data):
    if latest_environment["temperature"] is None:
        ui.send_message("analysis_error", {
            "message": "Waiting for valid sensor readings. Check the DHT11 connection.",
        })
        return

    ui.send_message("analysis_status", {"state": "analyzing"})

    prompt = (
        "Analyze these current room readings:\n"
        f"Temperature: {latest_environment['temperature']:.1f} °C\n"
        f"Humidity: {latest_environment['humidity']:.1f}% RH\n"
        f"Relative light level: {latest_environment['light_percent']}% "
        f"({latest_environment['light_label']})"
    )

    try:
        raw_response = "".join(llm.chat_stream(message=prompt))
        analysis = parse_analysis(raw_response)
    except Exception as error:
        print(f"[LLM ERROR] {type(error).__name__}: {error}", flush=True)
        ui.send_message("analysis_error", {
            "message": "Please configure your API Key and try again.",
        })
        return

    print(
        f"[AI] {analysis['status']} — {analysis['summary']} "
        f"Suggestion: {analysis['suggestion']}",
        flush=True,
    )
    ui.send_message("analysis_result", analysis)


ui.on_message("request_state", request_state)
ui.on_message("analyze_environment", analyze_environment)

print("AI Environment Advisor ready — waiting for sensor data.", flush=True)

App.run()
