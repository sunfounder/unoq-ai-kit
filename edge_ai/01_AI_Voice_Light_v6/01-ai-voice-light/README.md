# 01 AI Voice Light — V6

Create a hands-free voice-controlled RGB light. The Edge AI wake-word model continuously waits for **“Hey Arduino”**. After the wake word is detected, the assistant replies **“I'm here”**, automatically records one command, changes the light, and returns to standby.

This version has no Web UI, buttons, or LED matrix. All status information is printed in the Python console.

## What you need

- Arduino UNO Q
- USB microphone or USB headset with microphone
- Speaker or audio output device
- Common-cathode RGB LED
- Three 220 Ω resistors
- Internet connection for Edge TTS

## Wiring

| RGB LED pin | Arduino pin |
|---|---|
| Red | D8 through 220 Ω |
| Green | D7 through 220 Ω |
| Blue | D6 through 220 Ω |
| Common cathode | GND |

## How it works

1. Wait until the Python console shows `[READY]`.
2. Say **“Hey Arduino”**.
3. After the assistant says **“I'm here”**, immediately speak one light command.
4. The assistant listens for four seconds, executes the command, confirms it, and returns to standby.

No button needs to be pressed during normal use.

## Supported commands

- `Turn the light red.`
- `Turn the light green.`
- `Turn the light blue.`
- `Turn the light yellow.`
- `Turn the light purple.`
- `Turn the light white.`
- `Turn the light on.`
- `Turn the light off.`

## Console example

```text
[READY] Waiting for "Hey Arduino"...
[WAKE] "Hey Arduino" detected.
[TTS] I'm here.
[LISTENING] Speak a command now...
[RECOGNIZING] Processing speech...
[HEARD] Turn the light blue.
[ACTION] Light changed to blue.
[TTS] The light is now blue.
[READY] Waiting for "Hey Arduino"...
```

## Notes

- Keyword Spotting listens continuously, but full STT runs only after the wake word. This makes the interaction faster and avoids continuously transcribing room audio.
- The first startup can take a little longer because the local STT model is loaded before `[READY]` appears. Once ready, the first spoken command does not need to load the model again.
- Speak the command only after hearing **“I'm here”**.
- A quiet room and a microphone placed near the speaker improve recognition.
- If the LED is common-anode instead of common-cathode, the brightness logic must be inverted.
