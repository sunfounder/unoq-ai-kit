import time

from arduino.app_utils import App
from sunfounder_tts import EdgeTTS

tts = EdgeTTS()
tts.set_voice("en-US-JennyNeural")
tts.set_volume(50)

print("Speaking...")
tts.say("Hello! Welcome to Arduino App Lab.")
print("Done.")


def loop():
    time.sleep(10)


App.run(user_loop=loop)
