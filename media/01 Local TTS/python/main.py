import time
# import os

from arduino.app_utils import App
from sunfounder_tts import EdgeTTS


# os.makedirs("./audio_output", exist_ok=True)

tts = EdgeTTS(gain=0.4)
tts.set_voice("en-US-JennyNeural")



print("Speaking...")
tts.say("Hello! Welcome to Arduino App Lab.")
print("Done.")

def loop():
    time.sleep(10)

App.run(user_loop=loop)