"""AI Voice Light V6: hands-free wake word and RGB LED control."""

import queue
import threading
import time

from arduino.app_utils import App, Bridge
from arduino.app_bricks.keyword_spotting import KeywordSpotting
from sunfounder_stt import STT
from sunfounder_tts import EdgeTTS


LISTEN_SECONDS = 4.0

COLOR_PRESETS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "purple": (160, 32, 240),
    "white": (255, 255, 255),
}

wake_queue = queue.Queue(maxsize=1)
assistant_busy = False
system_ready = False
last_color = COLOR_PRESETS["white"]

stt = None
tts = None
spotter = None


def set_light(red, green, blue):
    """Send one RGB value to the Arduino sketch."""
    Bridge.call("set_rgb", int(red), int(green), int(blue))


def normalize_text(text):
    return " ".join(str(text).lower().strip().split())


def run_command(text):
    """Execute a supported light command and return its spoken reply."""
    global last_color

    command = normalize_text(text)

    off_phrases = ("light off", "turn off the light", "turn the light off")
    if any(phrase in command for phrase in off_phrases):
        set_light(0, 0, 0)
        return "The light is off.", "Light turned off."

    for name, color in COLOR_PRESETS.items():
        if name in command:
            last_color = color
            set_light(*color)
            return f"The light is now {name}.", f"Light changed to {name}."

    on_phrases = ("light on", "turn on the light", "turn the light on")
    if any(phrase in command for phrase in on_phrases):
        set_light(*last_color)
        return "The light is on.", "Light turned on."

    return None, None


def listen_for_command():
    """Record a short command and return the recognized text."""
    print("[LISTENING] Speak a command now...", flush=True)
    stt.reset()
    stt.start_listening()
    time.sleep(LISTEN_SECONDS)
    stt.stop_listening()

    print("[RECOGNIZING] Processing speech...", flush=True)
    result = stt.get_result(timeout=60)
    if isinstance(result, dict):
        result = result.get("text", "")
    return str(result).strip() if result else ""


def on_keyword_detected():
    """Queue one interaction and ignore repeat triggers while busy."""
    if not system_ready or assistant_busy or not wake_queue.empty():
        return
    try:
        wake_queue.put_nowait(True)
    except queue.Full:
        pass


def assistant_worker():
    """Handle each wake word without blocking the detector callback."""
    global assistant_busy

    while True:
        wake_queue.get()
        assistant_busy = True

        try:
            print('[WAKE] "Hey Arduino" detected.', flush=True)
            print("[TTS] I'm here.", flush=True)
            tts.say("I'm here.")

            # A short pause prevents the assistant's own reply from entering STT.
            time.sleep(0.2)
            recognized = listen_for_command()
            print(f"[HEARD] {recognized or '[no speech detected]'}", flush=True)

            if not recognized:
                reply = "I did not hear a command."
                print("[NO SPEECH] No command was detected.", flush=True)
            else:
                reply, action = run_command(recognized)
                if reply:
                    print(f"[ACTION] {action}", flush=True)
                else:
                    reply = "No supported light command was found."
                    print("[UNSUPPORTED] No supported light command was found.", flush=True)

            print(f"[TTS] {reply}", flush=True)
            tts.say(reply)

        except Exception as error:
            print(f"[ERROR] {error}", flush=True)
        finally:
            assistant_busy = False
            wake_queue.task_done()
            print('[READY] Waiting for "Hey Arduino"...', flush=True)


def initialize_services():
    """Load speech services, then enable continuous wake-word detection."""
    global stt, tts, spotter, system_ready

    try:
        print("[STARTING] Loading local speech recognition...", flush=True)
        stt = STT(type="local_fast", language="en")
        # Load the STT model now, so the first command does not pay startup time.
        stt.reset()

        print("[STARTING] Initializing text to speech...", flush=True)
        tts = EdgeTTS()
        tts.set_voice("en-US-JennyNeural")
        tts.set_volume(50)

        print("[STARTING] Starting wake-word detection...", flush=True)
        spotter = KeywordSpotting()
        spotter.on_detect("hey_arduino", on_keyword_detected)

        system_ready = True
        print('[READY] Waiting for "Hey Arduino"...', flush=True)

    except Exception as error:
        print(f"[STARTUP ERROR] {error}", flush=True)


threading.Thread(target=assistant_worker, daemon=True).start()
threading.Thread(target=initialize_services, daemon=True).start()

App.run()
