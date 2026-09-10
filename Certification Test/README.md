# Certification Test

Verifies every peripheral on the UNO Q with one automatic test sequence: IMU, PIR, ultrasonic, joystick, two servos, one motor, the speaker, and the camera.

## Hardware

- Pan Tilt Kit ×1
- Ultrasonic module ×1
- PIR motion sensor ×1
- DHT11 temperature and humidity module ×1
- Joystick module ×1
- USB-C cable ×1

## Wiring

| Component | UNO Q |
|-----------|-------|
| Motor IN1 | D2 |
| Motor IN2 | D3 |
| Ultrasonic TRIG | D4 |
| Ultrasonic ECHO | D5 |
| Ultrasonic VCC | 3.3V |
| Ultrasonic GND | GND |
| PIR OUT | D6 |
| PIR VCC | 3.3V |
| PIR GND | GND |
| Joystick X | A3 |
| Joystick Y | A2 |
| Joystick SW | D7 |
| Joystick VCC | 3.3V |
| Joystick GND | GND |
| DHT11 DATA | D8 |
| DHT11 VCC | 3.3V |
| DHT11 GND | GND |
| Pan servo | D9 |
| Tilt servo | D10 |
| IMU | QWIIC connector |

The speaker and camera are built into the Multimedia Carrier.

## How to Use

1. Open **Arduino App Lab**.
2. Select **Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `Certification Test.zip` from `unoq-ai-kit`.
4. Click **Run**.
5. The test sequence runs automatically. For the PIR test, wave your hand in front of the sensor when prompted. For the joystick test, move the stick and press it down. For the servo, motor, and speaker tests, confirm the physical result matches the printed CHECK message.
6. The summary line at the end shows `PASS` / `FAIL` / `CHECK` for all 8 tests.

## Test List

1. **IMU** — automatic: accelerometer and gyroscope values
2. **PIR** — wave your hand within 10 seconds
3. **Ultrasonic** — automatic: distance in cm
4. **DHT11** — automatic: temperature and humidity
5. **Joystick** — move the stick and press it down
6. **Servos** — CHECK: both sweep and return to center
7. **Motor** — CHECK: forward 2 s, reverse 2 s, stop
8. **Speaker** — CHECK: TTS plays "Speaker test one two three."
9. **Camera** — automatic: photo saved to `photos/certification_test.jpg`
