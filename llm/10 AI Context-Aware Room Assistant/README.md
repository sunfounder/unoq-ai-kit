# 10 AI Context-Aware Room Assistant

Click **SPEAK** once and describe the atmosphere you want. The app records for four seconds, displays the recognized speech, reads the room sensors, and asks an LLM to create an RGB lighting scene. TTS then explains the choice. The dashboard uses the same two-column visual structure as the smart-room project, while the speech workflow follows the proven online STT design from the show-and-tell project.

## Hardware and Wiring

| Module | Connection |
| --- | --- |
| PIR OUT | D4 |
| DHT11 DATA | D5 |
| RGB LED Red | D6 |
| RGB LED Green | D7 |
| RGB LED Blue | D8 |
| CSI Camera | CSI camera connector |

The RGB LED is treated as common cathode.

## Try Saying

- “Create a relaxing atmosphere.”
- “I'm in a bad mood.”
- “I need to study for an hour.”
- “Choose a light based on the room temperature.”
- “Create a sunset atmosphere.”
- “Make an energy-saving scene.”

## Interaction Flow

1. Select **SPEAK**.
2. Speak naturally during the four-second countdown.
3. Online STT displays the recognized request.
4. The dashboard updates DHT11 and PIR readings approximately every four seconds. During an AI request, background polling pauses so it cannot interfere with speech or RGB commands.
5. The LLM selects a scene, RGB percentages, and brightness.
6. The Arduino applies the scene and TTS explains the decision.
7. You can take over the light yourself at any time: drag the color wheel, move the brightness slider, or flip the **Room Light** switch. The next AI scene replaces your color.

## Run the App

1. Import the ZIP into Arduino App Lab.
2. Connect the hardware using the table above.
3. Enter the API key for **Cloud LLM**.
4. Enter an OpenAI API key for **OpenAI Speech to Text**.
5. Run the app and open **App Launch**.
6. Select **SPEAK**, then begin speaking immediately.

## Dashboard

- **Room Camera:** continuous live preview, independent from speech processing.
- **Environment:** current DHT11 temperature and humidity.
- **Occupancy:** current PIR motion state.
- **AI Lighting Scene:** the scene name plus an adjustable light control — a color wheel to drag, a brightness slider, a **Room Light** switch, and live RGB / hex readouts. The AI moves it whenever it applies a scene.
- **You Said:** the exact text returned by online speech recognition.
- **AI Explanation:** the reason spoken by TTS.

If a sensor is disconnected, its card shows **Unavailable** or **Unknown** instead of stopping the rest of the app.

This lesson differs from direct light control because the user describes an intention or atmosphere instead of naming a fixed color. The LLM combines that request with real sensor context and explains its hardware decision.
