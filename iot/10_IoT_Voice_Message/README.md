# 10 IoT Voice Message

Record a real voice message with the UNO Q microphone, view the live audio level in the Web UI, then play the recording through the speaker.

## How It Works

- **sunfounder_stt** handles microphone input. This lesson uses its recording API only, so speech recognition is not performed.
- **sunfounder_tts** handles speaker output. This lesson uses its audio playback API to play the recorded WAV file.

## Try It

1. Click **Record** and speak into the microphone.
2. Watch the live audio level while recording.
3. Click **Stop** to save the recording.
4. Click **Play** to hear the recorded message through the speaker.
5. Click **Pause** to pause playback, then click **Play** again to resume.

## Speaker Volume

The example initializes the speaker with:

```python
tts = EdgeTTS()
tts.set_volume(50)
```

Change the value passed to `set_volume()` if you want a different playback volume.

## About STT Models

This lesson does not perform speech recognition, so local Whisper model files are not included. The recording API can use the microphone without loading an STT model.
