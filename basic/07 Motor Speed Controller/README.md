# 07 Motor Speed Controller

Drive a DC motor with speed and direction control using the Robot Shield's H-bridge. The motor spins forward at 50% power for 3 seconds, brakes for 1 second, reverses for 3 seconds, then brakes again — demonstrating both speed control (PWM) and direction reversal (polarity switching).



## Libraries Used

- **RobotShield** library


## Hardware

- Pan Tilt Kit ×1
- DC motor ×1
- Fan blade (optional)
- USB-C cable ×1


## Wiring

Connect the DC motor to the Robot Shield's M0 terminal and the battery pack to the Robot Shield.

![Wiring Diagram](assets/docs_assets/wiring_motor.png)

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **My Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `07 Motor Speed Controller.zip` from `unoq-ai-kit\basic`.
5. Connect the battery pack to the Robot Shield.
6. Click **Run**.
7. The motor spins forward 3 s → brakes 1 s → reverses 3 s → brakes 3 s → repeats. Attach the fan blade to see and feel the airflow change direction.

## How it Works

**Flow**

- `setup()` — starts the Serial Monitor, initializes the I2C bus, and initializes the motor on port M0
- `loop()` — runs the sequence forward 3 s, brake 1 s, reverse 3 s, brake 3 s, then repeats

**Direction through the H-bridge**

`motor.setPower(50)` drives the motor forward at 50% power; `motor.setPower(-50)` reverses the voltage polarity through the Robot Shield's H-bridge, spinning it backward. Speed is a percentage (−100 to 100), not a raw PWM value — the `Motor` class handles the conversion.

**Braking**

`motor.setPower(0)` doesn't just remove power — the H-bridge shorts the motor terminals, which stops the motor quickly instead of letting it coast.

