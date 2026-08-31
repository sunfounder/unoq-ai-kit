# 05 IoT Voice Announcer

Type a message in the Web UI and let Arduino UNO Q speak it through the speaker.

## What it does

1. Open the Web UI shown by Arduino App Lab.
2. Enter a short message.
3. Click **Speak**.
4. The message is sent to the Python app and converted to speech with the SunFounder TTS brick.
5. UNO Q plays the generated speech through the speaker.

The example uses **EdgeTTS**, so the UNO Q needs Internet access for speech generation.
