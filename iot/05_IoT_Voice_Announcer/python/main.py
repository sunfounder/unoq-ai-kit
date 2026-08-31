from arduino.app_utils import App
from arduino.app_bricks.web_ui import WebUI
from sunfounder_tts import EdgeTTS

# Initialize Text-to-Speech.
# gain=1.0 keeps the original playback level.
tts = EdgeTTS(gain=1.0)
tts.set_voice("en-US-JennyNeural")

# Initialize Web UI.
ui = WebUI()


def speak_message(client, data):
    """Speak text received from the Web UI."""
    text = str(data.get("text", "")).strip()

    if not text:
        ui.send_message(
            "speak_status",
            {"state": "error", "message": "Please enter a message."},
            client,
        )
        return

    # Keep the example short and prevent accidentally sending huge messages.
    text = text[:300]

    ui.send_message(
        "speak_status",
        {"state": "speaking", "message": "Speaking..."},
        client,
    )

    try:
        tts.say(text)
        ui.send_message(
            "speak_status",
            {"state": "ready", "message": "Ready to speak another message."},
            client,
        )
    except Exception as error:
        print(f"TTS error: {error}")
        ui.send_message(
            "speak_status",
            {"state": "error", "message": "Unable to play the message."},
            client,
        )


ui.on_message("speak_message", speak_message)

print("=== IoT Voice Announcer ===")
print("Open the Web UI, type a message, and click Speak.")

App.run()
