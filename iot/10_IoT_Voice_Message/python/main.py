import threading
import time

from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from sunfounder_stt import STT
from sunfounder_tts import EdgeTTS

ui = WebUI()

# STT brick owns microphone input.  This lesson uses only its recording API,
# so no speech-recognition model is loaded.
stt = STT(type="online", language="en")

# TTS brick owns speaker output.  Here it plays an existing WAV file; no TTS
# synthesis is needed for the recorded message.
tts = EdgeTTS()
tts.set_volume(50)

recording = False
has_recording = False
recording_started = 0.0
recording_duration = 0.0
RECORDING_FILE = "/app/audio_shared/stt_last.wav"


def status_payload():
    state = "recording" if recording else tts.get_playback_state()
    return {
        "state": state,
        "level": 0,
        "duration": recording_duration,
        "has_recording": has_recording,
    }


def start_recording(client, data):
    global recording, has_recording, recording_started, recording_duration
    try:
        tts.stop_audio()
        stt.start_recording()
        recording = True
        has_recording = False
        recording_started = time.time()
        recording_duration = 0.0
        ui.send_message("voice_status", status_payload(), client)
    except Exception as error:
        print(f"Record start error: {error}", flush=True)
        ui.send_message("voice_error", {"message": "Unable to start recording."}, client)


def stop_recording(client, data):
    global recording, has_recording, recording_duration
    recording = False
    try:
        result = stt.stop_recording(RECORDING_FILE)
        recording_duration = float(result.get("duration", 0.0))
        has_recording = result.get("status") == "ready"
        ui.send_message("voice_status", status_payload(), client)
    except Exception as error:
        print(f"Record stop error: {error}", flush=True)
        ui.send_message("voice_error", {"message": "Unable to save the recording."}, client)


def play_recording(client, data):
    if not has_recording:
        return
    try:
        state = tts.get_playback_state()
        if state == "paused":
            tts.resume_audio()
        else:
            tts.play_audio(RECORDING_FILE)
        ui.send_message("voice_status", status_payload(), client)
    except Exception as error:
        print(f"Playback error: {error}", flush=True)
        ui.send_message("voice_error", {"message": "Unable to play the recording."}, client)


def pause_recording(client, data):
    try:
        tts.pause_audio()
        ui.send_message("voice_status", status_payload(), client)
    except Exception as error:
        print(f"Playback pause error: {error}", flush=True)
        ui.send_message("voice_error", {"message": "Unable to pause playback."}, client)


def level_worker():
    global recording_duration
    last_state = None
    while True:
        try:
            if recording:
                recording_duration = max(0.0, time.time() - recording_started)
                level = float(stt.get_audio_level()) / 100.0
                ui.send_message("voice_level", {
                    "state": "recording",
                    "level": level,
                    "duration": recording_duration,
                    "has_recording": False,
                })
                time.sleep(0.12)
            else:
                state = tts.get_playback_state()
                if state != last_state:
                    ui.send_message("voice_status", status_payload())
                    last_state = state
                time.sleep(0.25)
        except Exception as error:
            print(f"Audio status error: {error}", flush=True)
            time.sleep(0.5)


ui.on_message("record_start", start_recording)
ui.on_message("record_stop", stop_recording)
ui.on_message("play_recording", play_recording)
ui.on_message("pause_recording", pause_recording)

threading.Thread(target=level_worker, daemon=True).start()

print("=== IoT Voice Message ===", flush=True)
print("Microphone: sunfounder_stt recording API", flush=True)
print("Speaker: sunfounder_tts audio playback API", flush=True)

App.run()
