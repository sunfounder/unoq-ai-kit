# 09 AI Show and Tell

Place an object in front of the camera, hold the button on the Web UI, and ask a question about it. Online GPT speech-to-text converts the question into text, a vision-capable LLM examines the captured image, and text-to-speech reads the answer aloud.

## What You Will Learn

- Record speech with a hold-to-speak web control.
- Convert live speech into text using online GPT STT.
- Combine a spoken question with a camera image.
- Use a vision-capable LLM for multimodal question answering.
- Display and narrate the AI response.

## Hardware

- Arduino UNO Q
- RobotShield
- USB camera
- RobotShield microphone and speaker

No external button is required. The hold-to-speak button is on the Web UI.

## How It Works

1. The camera continuously displays a 640 × 480 live preview.
2. Place an object clearly in front of the camera.
3. Hold **HOLD TO SPEAK** and ask a question.
4. Release the button when you finish speaking.
5. The app captures the current camera image and sends the recording to online GPT STT.
6. The recognized question and captured image are sent to the vision-capable LLM.
7. The Web UI displays the question and answer.
8. TTS reads the answer aloud.

Example questions:

- What is this?
- What color is it?
- What can I use it for?
- Tell me something interesting about it.
- Is this object safe for a young child?

## Run the App

1. Import the app ZIP into Arduino App Lab.
2. Connect the USB camera.
3. In Brick Configuration, enter the API key for **Cloud LLM**.
4. Enter an OpenAI API key for **sunfounder_stt**. The same OpenAI key can be entered in both fields.
5. Make sure the UNO Q has internet access.
6. Select **RUN**, then open **App Launch**.
7. Hold the blue button while speaking and release it to submit the question.

## Interface States

| State | Meaning |
| --- | --- |
| Listening | The microphone is recording |
| Recognizing Speech | Online STT is transcribing the recording |
| AI Is Looking | The LLM is examining the captured image |
| Speaking | TTS is reading the answer |
| Ready | You can ask another question |

## Tips

- Speak after the page changes to **Listening**.
- Keep holding the button until the full question is finished.
- Recording stops automatically after 15 seconds if the button is not released.
- Keep the object near the center of the image.
- Use a plain background and bright, even lighting.
- The camera image is corrected vertically in the Python program.
- Camera capture runs in its own thread so speech and AI tasks do not block the live preview.
- If STT returns no text, move closer to the microphone and try again.
- STT, vision analysis, and TTS require an internet connection.
