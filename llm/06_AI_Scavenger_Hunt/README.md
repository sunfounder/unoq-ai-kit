# 06 AI Scavenger Hunt

Let AI create a scavenger-hunt mission, show an object to the camera, and ask
the AI referee to decide whether it matches. The RGB LED, buzzer, Web UI, and
TTS make the result easy to see and hear.

## What You Will Learn

- Generate a safe game mission with an LLM.
- Send a camera frame and a mission to a vision-capable cloud model.
- Request and parse structured JSON from an AI model.
- Control an RGB LED and buzzer from Python through Bridge.
- Track a game score and attempts in a Web UI.

## Hardware

- Arduino UNO Q
- USB camera
- RobotShield speaker or another supported audio output
- Common-cathode RGB LED
- 220 ohm resistors x3
- Active or passive buzzer
- Jumper wires

## Wiring

| Component | UNO Q / RobotShield pin |
|---|---|
| RGB red through 220 ohm | D8 |
| RGB green through 220 ohm | D7 |
| RGB blue through 220 ohm | D6 |
| RGB common cathode | GND |
| Buzzer signal | D5 |
| Buzzer ground | GND |

## Feedback

| Game state | RGB LED | Buzzer |
|---|---|---|
| Mission active | Yellow | Off |
| Mission complete | Green | Two high tones |
| Try again | Red | One low tone |
| Game reset | Off | Off |

## How It Works

1. **NEW MISSION** asks the LLM to create a safe challenge.
2. TTS reads the mission aloud and the RGB LED turns yellow.
3. The player shows one object to the USB camera.
4. **CHECK OBJECT** sends the current frame and mission to the vision-capable
   LLM.
5. A match turns the RGB LED green, plays two high tones, and adds one point.
6. A mismatch turns the RGB LED red, plays one low tone, and allows another
   attempt.

## Run the App

1. Wire the RGB LED and buzzer as shown above.
2. Connect the USB camera and speaker.
3. Import the ZIP file into Arduino App Lab.
4. Enter your OpenAI API key in the **Cloud LLM** Brick configuration.
5. Click **Run**, then open **App Launch**.
6. Click **NEW MISSION** and listen to the task.
7. Place one matching object near the center of the camera.
8. Click **CHECK OBJECT**.

If the object matches, the score increases. If it does not match, you can show
another object and try the same mission again.

## Example Missions

- Find something red.
- Find something used for writing.
- Find something with a round shape.
- Find something made of paper.

## Tips

- Keep only one main object in front of the camera.
- Use bright, even lighting and a simple background.
- Make sure the full object is visible before checking it.
- The program flips the camera source vertically before preview and AI
  analysis to correct the camera's physical orientation.
- AI can make mistakes. The game is intended for learning and entertainment.
- An internet connection is required for Cloud LLM and Edge TTS.
