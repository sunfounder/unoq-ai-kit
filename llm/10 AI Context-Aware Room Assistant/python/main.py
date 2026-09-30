# SPDX-License-Identifier: MPL-2.0
"""10 AI Context-Aware Room Assistant."""
import json, os, re, threading, time
import cv2
from fastapi.responses import StreamingResponse
from arduino.app_bricks.cloud_llm import CloudLLM
from arduino.app_bricks.web_ui import WebUI
from arduino.app_peripherals.camera import Camera
from arduino.app_utils import App, Bridge, Logger
from sunfounder_stt import STT
from sunfounder_tts import EdgeTTS

try:
    from robot_shield import setup_audio_output
except ImportError:
    setup_audio_output = None

RECORD_SECONDS, SENSOR_TIMEOUT = 4, 1.5
SYSTEM_PROMPT = (
    "You are a warm, thoughtful room-atmosphere assistant. The user says what they are "
    "doing or how they feel, and you turn that into one RGB lighting scene.\n"
    "Decide the mood first, then the light:\n"
    "- sad, stressed, angry, upset, or in a bad mood -> soft warm amber, low brightness "
    "(about 100/45/10 at brightness 25)\n"
    "- wants to relax, unwind, sleep, or rest -> deep warm dim (about 90/35/15 at brightness 15)\n"
    "- reading, studying, working, or focusing -> cool neutral bright (about 60/80/100 at brightness 85)\n"
    "- happy, excited, celebrating, or a party -> vivid saturated colour (about 100/20/90 at brightness 90)\n"
    "- cozy, romantic, or wanting warmth -> warm low light (about 100/40/20 at brightness 30)\n"
    "- no mood and no clear request -> choose a comfortable neutral scene and explain why\n"
    "Use the real temperature, humidity and motion readings as extra context: a hot room "
    "suits a cooler colour, a dark room suits lower brightness, and motion means somebody "
    "is actually there. Ignore readings that are unavailable.\n"
    "Return only valid JSON with exactly these keys:\n"
    "{\"scene\":\"<two or three words>\",\"red\":<0-100>,\"green\":<0-100>,"
    "\"blue\":<0-100>,\"brightness\":<0-100>,\"reply\":\"<one short sentence>\"}\n"
    "That example is a format placeholder only - never reuse its values.\n"
    "Write reply in the same language as the user's request sentence - answer in "
    "Chinese if the user wrote Chinese, in Spanish if they wrote Spanish, and in "
    "English when the request is English or when the language is unclear.\n"
    "reply must be one short sentence that responds to what the user actually said - "
    "not a report of what you did."
)
logger, ui = Logger("AIContextAwareRoomAssistant"), WebUI()
if setup_audio_output:
    try: setup_audio_output()
    except Exception as error: logger.warning(f"Audio mixer setup unavailable: {error}")

stt = STT(type="online", language="en")
stt_key = os.environ.get("OPENAI_API_KEY", "").strip() or os.environ.get("API_KEY", "").strip()
if stt_key: STT.API_KEY = stt_key
llm = CloudLLM(model="openai:gpt-4o-mini", system_prompt=SYSTEM_PROMPT, temperature=0.5, max_tokens=180)
llm.with_memory(max_messages=0)
tts = EdgeTTS(); tts.set_voice("en-US-JennyNeural"); tts.set_volume(50)
camera = Camera(fps=10)

frame_lock, state_lock, bridge_lock = threading.Lock(), threading.Lock(), threading.Lock()
current_frame, busy = None, False
current_state, current_message = "ready", "Select SPEAK and describe the atmosphere you want."
last_heard = last_reply = ""
scene_data = {"scene":"READY","red":0,"green":0,"blue":0,"brightness":0}
last_nonzero_light = {"red":30,"green":65,"blue":100,"brightness":85}
sensor_data = {"temperature":"Unavailable","humidity":"Unavailable","motion":"UNKNOWN"}

def snapshot():
    with state_lock:
        return {"state":current_state,"message":current_message,"heard":last_heard,
                "reply":last_reply,"busy":busy,**sensor_data,**scene_data}

def send_status(state=None, message=None, room=None, heard=None, reply=None, seconds=None):
    global current_state, current_message, last_heard, last_reply
    with state_lock:
        if state is not None: current_state = state
        if message is not None: current_message = message
        if heard is not None: last_heard = heard
        if reply is not None: last_reply = reply
        payload = {"state":current_state,"message":current_message,"heard":last_heard,
                   "reply":last_reply,"busy":busy,"seconds":seconds,**sensor_data,**scene_data}
    ui.send_message("assistant_status", payload, room=room)
    if state is not None: print(f"[ASSISTANT] {state.upper()}: {current_message}")

def generate_frames():
    while True:
        with frame_lock: frame = current_frame
        if frame is None: time.sleep(.1); continue
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        time.sleep(.1)

def video_stream():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

def camera_loop():
    global current_frame
    while True:
        try:
            frame = camera.capture()
            if frame is not None:
                frame = cv2.flip(frame, 0)
                ok, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                if ok:
                    with frame_lock: current_frame = encoded.tobytes()
        except Exception as error:
            logger.warning(f"Camera frame unavailable: {error}"); time.sleep(.25)
        time.sleep(.08)

def safe_bridge_call(service, value="", default=None):
    try:
        with bridge_lock: return Bridge.call(service, value, timeout=SENSOR_TIMEOUT)
    except Exception as error:
        logger.warning(f"{service} unavailable: {error}"); return default

def read_environment(push=True):
    dht, motion = safe_bridge_call("read_dht", "", "ERROR"), safe_bridge_call("read_pir", "", -1)
    temperature = humidity = "Unavailable"
    if isinstance(dht, str):
        match = re.search(r"T=([-\d.]+),H=([-\d.]+)", dht)
        if match: temperature, humidity = f"{match.group(1)} °C", f"{match.group(2)} %"
    motion_text = "DETECTED" if motion == 1 else "CLEAR" if motion == 0 else "UNKNOWN"
    with state_lock: sensor_data.update(temperature=temperature, humidity=humidity, motion=motion_text)
    if push: send_status()
    return dict(sensor_data)

def sensor_loop():
    while True:
        with state_lock: app_busy = busy
        if not app_busy: read_environment(push=True)
        time.sleep(4)

def extract_text(result):
    if isinstance(result, dict): result = result.get("text", "")
    return str(result or "").strip()

def parse_scene(response):
    match = re.search(r"\{.*\}", extract_text(response), flags=re.DOTALL)
    if not match: raise ValueError("The AI did not return scene JSON.")
    data = json.loads(match.group(0))
    def pct(name):
        try: return max(0, min(100, int(data.get(name, 0))))
        except (TypeError, ValueError): return 0
    return {"scene":" ".join(str(data.get("scene","Custom Scene")).split())[:40],
            "red":pct("red"),"green":pct("green"),"blue":pct("blue"),
            "brightness":pct("brightness"),
            "reply":" ".join(str(data.get("reply","Your scene is ready.")).split())[:220]}

def apply_scene(scene):
    values = f"{scene['red']},{scene['green']},{scene['blue']},{scene['brightness']}"
    if safe_bridge_call("set_rgb_scene", values, 0) != 1: raise RuntimeError("The RGB light did not respond.")
    with state_lock:
        scene_data.update({key:scene[key] for key in ("scene","red","green","blue","brightness")})
        if scene["red"] or scene["green"] or scene["blue"]:
            last_nonzero_light.update({key:scene[key] for key in ("red","green","blue","brightness")})

def clamp_pct(value):
    try: return max(0, min(100, int(round(float(value)))))
    except (TypeError, ValueError): return 0

def set_light(red, green, blue, brightness=None, scene="Your Colour"):
    """Apply a light value that came from the Web UI (every value 0-100)."""
    red, green, blue = clamp_pct(red), clamp_pct(green), clamp_pct(blue)
    if brightness is None:
        with state_lock: brightness = scene_data.get("brightness", 100)
    brightness = clamp_pct(brightness)
    # The app starts dark: a new colour with no brightness would stay invisible,
    # so choosing a colour also means choosing a visible light.
    if (red or green or blue) and not brightness: brightness = 100
    with state_lock:
        scene_data.update({"scene":scene,"red":red,"green":green,"blue":blue,"brightness":brightness})
        if red or green or blue:
            last_nonzero_light.update({"red":red,"green":green,"blue":blue,"brightness":brightness})
    if safe_bridge_call("set_rgb_scene", f"{red},{green},{blue},{brightness}", 0) != 1:
        logger.warning("The RGB light did not respond to the Web UI.")
    send_status()

def on_set_rgb_color(sid, data):
    set_light(data.get("r", 0), data.get("g", 0), data.get("b", 0))

def on_toggle_light(sid, data):
    if data.get("enabled"):
        with state_lock: light = dict(last_nonzero_light)
        set_light(light["red"], light["green"], light["blue"], light["brightness"], scene="Your Colour")
    else:
        with state_lock: brightness = scene_data.get("brightness", 0)
        set_light(0, 0, 0, brightness, scene="Light Off")

def process_request(sid):
    global busy
    request = ""
    try:
        for remaining in range(RECORD_SECONDS, 0, -1):
            send_status("listening", f"Listening... {remaining} second{'s' if remaining != 1 else ''} remaining.", room=sid, seconds=remaining)
            time.sleep(1)
        stt.stop_listening(); send_status("recognizing", "Converting your speech to text...", room=sid)
        request = extract_text(stt.get_result(timeout=45))
        if request.startswith("[STT ERROR]"): raise RuntimeError(request)
        if not request:
            send_status("ready", "No speech was recognized. Select SPEAK and try again.", room=sid, heard="No speech was recognized."); return
        request = request[:300]; print(f"[TRANSCRIPT] {request}")
        send_status("sensors", "Reading the room conditions...", room=sid, heard=request)
        env = read_environment(push=False)
        prompt = f"User request: {request}\nTemperature: {env['temperature']}\nHumidity: {env['humidity']}\nMotion: {env['motion']}"
        send_status("thinking", "AI is creating a lighting scene...", room=sid)
        scene = parse_scene(llm.chat(message=prompt))
        send_status("applying", "Applying the AI lighting scene...", room=sid); apply_scene(scene)
        send_status("speaking", "The assistant is explaining its choice...", room=sid, reply=scene["reply"])
        try: tts.say(scene["reply"])
        except Exception as error: logger.warning(f"TTS unavailable: {error}")
        send_status("ready", "Scene ready. Select SPEAK to create another atmosphere.", room=sid, heard=request, reply=scene["reply"])
    except Exception as error:
        logger.exception(f"Scene request failed: {error}")
        send_status("error", f"Request failed: {type(error).__name__}: {error}", room=sid, heard=request or None)
    finally:
        with state_lock: busy = False
        send_status(room=sid)

def start_scene_request(sid, _data):
    global busy
    with state_lock:
        if busy: return
        busy = True
    try:
        if not STT.API_KEY: raise RuntimeError("OpenAI STT API key is missing. Add it in Brick Configuration.")
        stt.reset(); stt.start_listening()
        threading.Thread(target=process_request, args=(sid,), daemon=True).start()
    except Exception as error:
        with state_lock: busy = False
        send_status("error", f"Unable to start recording: {type(error).__name__}: {error}", room=sid)

def send_current_state(sid, _data): ui.send_message("assistant_status", snapshot(), room=sid)

ui.expose_api("GET", "/stream", video_stream)
ui.on_message("start_scene_request", start_scene_request)
ui.on_message("get_state", send_current_state)
ui.on_message("set_rgb_color", on_set_rgb_color)
ui.on_message("toggle_light", on_toggle_light)
print("AI Context-Aware Room Assistant ready.")
print("Open App Launch, select SPEAK, and speak for four seconds.")
with camera:
    threading.Thread(target=camera_loop, daemon=True).start()
    threading.Thread(target=sensor_loop, daemon=True).start()
    App.run()
