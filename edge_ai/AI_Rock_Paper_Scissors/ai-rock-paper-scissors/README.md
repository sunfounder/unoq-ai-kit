# AI Rock Paper Scissors — V2

Play rock-paper-scissors against the computer using real-time AI hand gesture detection. Press **START GAME**, then hold rock, paper, or scissors in front of the camera. The Web UI displays both choices, keeps score, and shows the camera feed.

## AI Model

This project uses the **Hand gestures** model selected for the `Video Object Detection` Brick.

| Model gesture | Game action |
| --- | --- |
| Neutral / fist | Rock ✊ |
| Five / open hand | Paper ✋ |
| Peace / V-sign | Scissors ✌️ |

## Hardware Requirements

- Arduino UNO Q ×1
- Multimedia Carrier with CSI camera
- RGB LED (common cathode) ×1
- 220 Ω resistors ×3
- Buzzer ×1
- USB-C cable ×1

## Wiring

| Component | UNO Q |
| --- | --- |
| RGB LED Red anode | D8 through a 220 Ω resistor |
| RGB LED Green anode | D7 through a 220 Ω resistor |
| RGB LED Blue anode | D6 through a 220 Ω resistor |
| RGB LED Common cathode | GND |
| Buzzer (+) | D5 |
| Buzzer (−) | GND |

## Result Feedback

| Result | RGB LED | Buzzer |
| --- | --- | --- |
| Player wins | Green | Rising notes |
| Computer wins | Red | Low note |
| Tie | Blue | Two equal notes |

## Prerequisites

1. Open App Lab settings.
2. Enable the external carrier.
3. Configure the camera port as `type1-2lanes`.
4. Reboot the board.

## How to Play

1. Import `AI_Rock_Paper_Scissors_v2.zip` into Arduino App Lab.
2. Confirm that **Hand gestures** is shown as the model in use for the Video Object Detection Brick.
3. Click **Run** and open the Web UI.
4. Click **START GAME** to start a round.
5. During the countdown, prepare rock, paper, or scissors.
6. Hold the move steadily in front of the camera until it is detected.
7. Check the winner, light, sound, and updated score.

The gesture must remain above 45% confidence for about 0.25 seconds. This makes the game easier to trigger while still preventing one unstable frame from being counted.

The Python console prints the strongest raw model label and confidence every half second. This makes it easier to see whether the model is detecting the hand even when a move has not yet triggered.

## How It Works

```text
START GAME button → Countdown
Camera → Hand Gestures model → Stable ✊ / ✋ / ✌️ player move
                                                     ↓
                                           Random computer move
                                                     ↓
                                            Compare both choices
                                               │           │
                                               │           └── Web UI + score
                                               └── RGB LED + D5 buzzer
```

The AI recognizes the player's hand gesture. The computer's move is selected randomly; it is not generated or predicted by the AI model. The thumbs-up gesture is no longer required to begin a round.
