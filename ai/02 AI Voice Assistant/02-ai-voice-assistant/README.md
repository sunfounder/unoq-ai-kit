# 02 AI Voice Assistant

A minimal voice assistant example for Arduino App Lab and RobotShield.

## Workflow

```text
Hold the web button
        ↓
RobotShield microphone
        ↓
sunfounder_stt
        ↓
CloudLLM
        ↓
sunfounder_tts
        ↓
RobotShield speaker
```

## Important implementation details

The project uses the real APIs from:

- `sunfounder_stt`
- `sunfounder_tts`
- `robot_shield`

At startup it creates the audio directory required by both STT and TTS:

```python
os.makedirs("/app/audio_output", exist_ok=True)
os.makedirs("./audio_output", exist_ok=True)
```

It also configures the RobotShield microphone and speaker:

```python

setup_audio_output()
```

The physical USR button is not used.

## Default settings

```python
STT_LANGUAGE = "en"
STT_MODEL = "tiny"
TTS_VOICE = "en-US-JennyNeural"
```

For Chinese, change these values:

```python
STT_LANGUAGE = "zh"
TTS_VOICE = "zh-CN-XiaoxiaoNeural"
```

The first local STT run may take longer because the Whisper model is downloaded
and initialized.
