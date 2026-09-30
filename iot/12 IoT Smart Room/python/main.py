"""12 IoT Smart Room."""

import base64
import time
from pathlib import Path
from typing import Callable, Optional

import cv2

from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_peripherals.camera import Camera
from sunfounder_stt import STT
from sunfounder_tts import EdgeTTS

ui = WebUI()

STREAM_INTERVAL = 0.25
JPEG_QUALITY = 65
AUTO_FAN_ON_TEMP = 28.0
VOICE_LISTEN_SECONDS = 4.0

AUDIO_OUTPUT_DIR = Path("/app/audio_output")
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

latest_environment = {
    "temperature": None,
    "humidity": None,
    "motion": False,
    "light_raw": None,
    "light_percent": None,
    "light_label": "Waiting",
}
latest_pan_tilt = {"pan": 90, "tilt": 90}

system_running = True
fan_mode = "auto"
fan_enabled = False
rgb_color = {"r": 0, "g": 0, "b": 0}
last_nonzero_rgb = {"r": 255, "g": 255, "b": 255}
voice_requested = False
last_stream_time = 0.0

print("Loading local speech recognition...", flush=True)
stt = STT(type="local_fast", language="en")

print("Initializing speaker...", flush=True)
tts = EdgeTTS()


def configure_tts():
    """The TTS sidecar may still be registering its RPC when the app starts."""
    for attempt in range(6):
        try:
            tts.set_voice("en-US-JennyNeural")
            tts.set_volume(50)
            return True
        except Exception as exc:
            print(f"Speaker not ready ({exc}); retrying...", flush=True)
            time.sleep(2)
    print("Speaker unavailable - the app continues without speech.", flush=True)
    return False


configure_tts()

print("Initializing camera...", flush=True)
camera = Camera()
camera.start()
time.sleep(1)
print("IoT Smart Room ready.", flush=True)


def light_description(percent):
    if percent is None:
        return "Waiting"
    if percent < 25:
        return "Dark"
    if percent < 55:
        return "Dim"
    if percent < 80:
        return "Bright"
    return "Very Bright"


def send_camera_frame(frame):
    success, encoded = cv2.imencode(
        ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
    )
    if not success:
        return
    image_base64 = base64.b64encode(encoded.tobytes()).decode("ascii")
    ui.send_message("camera_frame", {"image": image_base64})


def environment_update(temperature, humidity, motion, light_raw):
    raw = max(0, min(1023, int(light_raw)))
    # Classroom-friendly relative brightness. If the user's LDR divider is
    # electrically reversed, this single mapping can be inverted later.
    percent = round(raw * 100 / 1023)

    latest_environment.update({
        "temperature": float(temperature),
        "humidity": float(humidity),
        "motion": bool(motion),
        "light_raw": raw,
        "light_percent": percent,
        "light_label": light_description(percent),
    })
    update_auto_fan()
    send_room_state()


Bridge.provide("environment_update", environment_update)


def read_angle(value, fallback):
    """Bridge returns text — fall back to the last known angle on garbage."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return fallback


def report_pan_tilt():
    """Push the current servo angles to every open Web UI."""
    ui.send_message("camera_control_update", dict(latest_pan_tilt))


def pan_step(delta):
    """Nudge the pan servo (positive = left, negative = right)."""
    latest_pan_tilt["pan"] = read_angle(
        Bridge.call("pan_step", int(delta)), latest_pan_tilt["pan"]
    )
    report_pan_tilt()


def tilt_step(delta):
    """Nudge the tilt servo (positive = down, negative = up)."""
    latest_pan_tilt["tilt"] = read_angle(
        Bridge.call("tilt_step", int(delta)), latest_pan_tilt["tilt"]
    )
    report_pan_tilt()


def pan_to(command, message):
    """Voice command: jump the pan servo to one of the presets."""
    latest_pan_tilt["pan"] = read_angle(
        Bridge.call(command, ""), latest_pan_tilt["pan"]
    )
    report_pan_tilt()
    tts.say(message)


def tilt_to(command, message):
    """Voice command: jump the tilt servo to one of the presets."""
    latest_pan_tilt["tilt"] = read_angle(
        Bridge.call(command, ""), latest_pan_tilt["tilt"]
    )
    report_pan_tilt()
    tts.say(message)


def center_pan_tilt(speak=False):
    """Put both servos back to 90 degrees."""
    Bridge.call("center", "")
    latest_pan_tilt["pan"] = 90
    latest_pan_tilt["tilt"] = 90
    report_pan_tilt()
    if speak:
        tts.say("Returning to center.")


def set_fan(enabled):
    global fan_enabled
    fan_enabled = bool(enabled)
    Bridge.call("set_fan_enabled", fan_enabled)


def set_rgb(r, g, b):
    global rgb_color, last_nonzero_rgb
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    rgb_color = {"r": r, "g": g, "b": b}
    if r or g or b:
        last_nonzero_rgb = dict(rgb_color)
    Bridge.call("set_rgb_color", r, g, b)


def update_auto_fan():
    if fan_mode != "auto":
        return
    temperature = latest_environment["temperature"]
    if temperature is None:
        return
    should_run = temperature >= AUTO_FAN_ON_TEMP
    if should_run != fan_enabled:
        set_fan(should_run)


def send_room_state(client=None):
    data = {
        **latest_environment,
        "system_running": system_running,
        "fan_mode": fan_mode,
        "fan_enabled": fan_enabled,
        "fan_power": 30,
        "auto_threshold": AUTO_FAN_ON_TEMP,
        "rgb": dict(rgb_color),
    }
    if client is None:
        ui.send_message("room_state", data)
    else:
        ui.send_message("room_state", data, client)


def on_toggle_system(client, data):
    global system_running
    system_running = bool(data.get("enabled", False))
    Bridge.call("set_system_running", system_running)
    send_room_state()


def on_set_fan_mode(client, data):
    global fan_mode
    fan_mode = "manual" if str(data.get("mode", "auto")).lower() == "manual" else "auto"
    if fan_mode == "auto":
        update_auto_fan()
    send_room_state()


def on_toggle_fan(client, data):
    if fan_mode != "manual":
        return
    set_fan(bool(data.get("enabled", False)))
    send_room_state()


def on_set_rgb_color(client, data):
    set_rgb(data.get("r", 0), data.get("g", 0), data.get("b", 0))
    send_room_state()


def on_toggle_light(client, data):
    if bool(data.get("enabled", False)):
        set_rgb(**last_nonzero_rgb)
    else:
        set_rgb(0, 0, 0)
    send_room_state()


def on_get_initial_state(client, data):
    send_room_state(client)
    ui.send_message("camera_control_update", dict(latest_pan_tilt), client)


def on_voice_control(client, data):
    global voice_requested
    voice_requested = True
    ui.send_message("voice_state", {"state": "listening"}, client)


PAN_STEP_DEGREES = 10
TILT_STEP_DEGREES = 10


def on_pan_tilt_move(client, data):
    """Web UI arrow keys: left/right/up/down nudge one step, center resets."""
    move = str((data or {}).get("move", "")).lower()

    try:
        if move == "left":
            pan_step(PAN_STEP_DEGREES)
        elif move == "right":
            pan_step(-PAN_STEP_DEGREES)
        elif move == "up":
            tilt_step(-TILT_STEP_DEGREES)
        elif move == "down":
            tilt_step(TILT_STEP_DEGREES)
        elif move == "center":
            center_pan_tilt()
    except Exception as exc:
        print(f"Pan-tilt move failed: {exc}", flush=True)


ui.on_message("toggle_system", on_toggle_system)
ui.on_message("set_fan_mode", on_set_fan_mode)
ui.on_message("toggle_fan", on_toggle_fan)
ui.on_message("set_rgb_color", on_set_rgb_color)
ui.on_message("toggle_light", on_toggle_light)
ui.on_message("get_initial_state", on_get_initial_state)
ui.on_message("voice_control", on_voice_control)
ui.on_message("pan_tilt_move", on_pan_tilt_move)


COLOR_PRESETS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "purple": (160, 32, 240),
    "cyan": (0, 255, 255),
    "white": (255, 255, 255),
    "orange": (255, 128, 0),
    "pink": (255, 80, 160),
}


def color_name():
    r, g, b = rgb_color["r"], rgb_color["g"], rgb_color["b"]
    if r == g == b == 0:
        return "off"
    for name, values in COLOR_PRESETS.items():
        if (r, g, b) == values:
            return name
    return "a custom color"


def build_status_message():
    t = latest_environment["temperature"]
    h = latest_environment["humidity"]
    motion = latest_environment["motion"]
    light = latest_environment["light_label"]

    if t is None or h is None:
        return "Room data is not ready yet."

    motion_text = "Motion is detected." if motion else "No motion is detected."
    fan_text = "The fan is on." if fan_enabled else "The fan is off."

    return (
        f"Temperature is {round(t)} degrees Celsius. "
        f"Humidity is {round(h)} percent. "
        f"The room is {light.lower()}. "
        f"{motion_text} {fan_text} "
        f"The room light is {color_name()}."
    )


def voice_fan_on():
    global fan_mode
    fan_mode = "manual"
    set_fan(True)
    send_room_state()
    tts.say("Fan turned on.")


def voice_fan_off():
    global fan_mode
    fan_mode = "manual"
    set_fan(False)
    send_room_state()
    tts.say("Fan turned off.")


def voice_light_on():
    set_rgb(**last_nonzero_rgb)
    send_room_state()
    tts.say("Room light turned on.")


def voice_light_off():
    set_rgb(0, 0, 0)
    send_room_state()
    tts.say("Room light turned off.")


def set_named_color(name):
    r, g, b = COLOR_PRESETS[name]
    set_rgb(r, g, b)
    send_room_state()
    tts.say(f"Room light set to {name}.")


def move_left():
    pan_to("pan_left", "Turning left.")


def move_right():
    pan_to("pan_right", "Turning right.")


def move_up():
    tilt_to("tilt_up", "Looking up.")


def move_down():
    tilt_to("tilt_down", "Looking down.")


def move_center():
    center_pan_tilt(speak=True)


def speak_status():
    tts.say(build_status_message())


COMMANDS = (
    (("fan on", "turn on the fan", "turn the fan on"), voice_fan_on),
    (("fan off", "turn off the fan", "turn the fan off"), voice_fan_off),
    (("light on", "turn on the light", "turn the light on"), voice_light_on),
    (("light off", "turn off the light", "turn the light off"), voice_light_off),
    (("look left", "turn left"), move_left),
    (("look right", "turn right"), move_right),
    (("look up", "turn up"), move_up),
    (("look down", "turn down"), move_down),
    (("center", "centre", "look forward"), move_center),
    (("system status", "room status", "status"), speak_status),
)


def match_command(text):
    normalized = " ".join(text.lower().strip().split())

    for color in COLOR_PRESETS:
        phrases = (
            f"set light {color}",
            f"set the light {color}",
            f"light {color}",
            f"make the light {color}",
        )
        if any(phrase in normalized for phrase in phrases):
            return lambda color=color: set_named_color(color)

    for phrases, action in COMMANDS:
        if any(phrase in normalized for phrase in phrases):
            return action

    return None


def run_voice_control():
    global voice_requested
    voice_requested = False

    try:
        # Stop the speaker first: the microphone sits right next to it, so
        # anything still playing would be recorded and ruin recognition.
        try:
            tts.stop_audio()
        except Exception:
            pass

        stt.reset()
        print("Listening...", flush=True)
        stt.start_listening()
        time.sleep(VOICE_LISTEN_SECONDS)
        stt.stop_listening()

        print("Recognizing...", flush=True)
        result = stt.get_result(timeout=60)
        if isinstance(result, dict):
            result = result.get("text", "")
        recognized = result.strip() if result else ""

        ui.send_message("voice_state", {"state": "ready", "text": recognized})

        if not recognized:
            print("No speech recognized.", flush=True)
            return

        print(f"Recognized: {recognized}", flush=True)
        action = match_command(recognized)
        if action is None:
            tts.say("Command not recognized.")
        else:
            action()

    except Exception as exc:
        print(f"Voice control error: {exc}", flush=True)
        ui.send_message(
            "voice_state",
            {"state": "ready", "text": "Voice control error"},
        )


def loop():
    global last_stream_time

    now = time.monotonic()
    if now - last_stream_time >= STREAM_INTERVAL:
        frame = camera.capture()
        frame = cv2.flip(frame, 0)
        send_camera_frame(frame)
        last_stream_time = now

    if voice_requested:
        run_voice_control()

    time.sleep(0.02)


try:
    App.run(user_loop=loop)
finally:
    try:
        set_fan(False)
        set_rgb(0, 0, 0)
        Bridge.call("set_system_running", False)
    except Exception:
        pass
    camera.stop()
