# IoT Control Center

Build a local IoT control center that combines the camera, environment sensors, 10-Axis IMU, physical joystick, pan-tilt servos, motor, and speaker in one project.

The project uses the UNO Q's local Web UI. It does **not** use Arduino Cloud, Telegram, Edge AI, or STT.

## Project Effect

The browser displays:

- Live camera preview
- DHT11 temperature and humidity
- Ultrasonic distance
- PIR motion status
- 10-Axis IMU data
- Physical joystick position
- Pan and tilt servo angles

The page also provides:

- **System Run** switch
- **Motor M0** switch

When the Motor switch is enabled while the system is running, M0 runs at **30% power**.

The speaker announces a short system summary every **2 minutes** using offline Espeak TTS.

## Final Wiring

| Module | UNO Q / Shield |
| --- | --- |
| DHT11 DATA | D5 |
| PIR OUT | D4 |
| Ultrasonic TRIG | D3 |
| Ultrasonic ECHO | D2 |
| Joystick X | A3 |
| Joystick Y | A2 |
| 10-Axis IMU | I2C / Wire1 |
| Motor | M0 |
| Pan Servo | P0 |
| Tilt Servo | P1 |
| Camera | CSI |
| Speaker | Multimedia Carrier audio output |

## Physical Joystick

The physical joystick uses the same control relationship as the tested Joystick Servo example:

```text
Joystick Y (A2) -> Pan Servo P0
Joystick X (A3) -> Tilt Servo P1
```

The pan and tilt angles are limited to:

```text
-45° to +45°
```

The Web UI displays the physical joystick position with a cross-shaped joystick indicator.

## Motor

The motor is controlled on the MCU using the RobotShield library:

```cpp
Motor motor("M0", 4, 5);
```

When the Web UI enables the motor:

```cpp
motor.setPower(30);
```

When disabled:

```cpp
motor.setPower(0);
```

## System Run

When **System Run** is ON:

- The joystick controls P0/P1
- The Motor switch can run M0 at 30%
- All sensor data and camera streaming continue

When **System Run** is OFF:

- M0 stops
- P0/P1 return to 0°
- Joystick movement no longer drives the servos
- Camera and sensor monitoring continue

## Camera

The camera uses the normal local Web Stream implementation:

```python
frame = camera.capture()
frame = cv2.flip(frame, 0)
```

The frame is compressed to JPEG and sent to the local Web UI. No object-detection or Edge AI Brick is used.

## Sensor Updates

The Arduino sketch reads:

```text
DHT11        every 2 seconds
PIR          with the environment update
Ultrasonic   with the environment update
Joystick     about every 60 ms
10-Axis IMU  every 500 ms
```

The data is sent to Python through Bridge and displayed in the browser.

## 10-Axis IMU

The IMU uses:

```cpp
#include "SunFounder_IMU.hpp"

SunFounder_IMU imu(&Wire1);
```

The project also includes `calibration_data.h`.

For best results, run the IMU calibration example first and replace the calibration values with the values measured by your own module.

## Offline Speaker Announcement

The project uses **Espeak**, not STT and not an online TTS service.

Every two minutes:

```python
SPEAK_INTERVAL = 120.0
```

the speaker announces a short status message such as:

```text
System status.
Temperature is 26 degrees Celsius.
Humidity is 58 percent.
No motion is detected.
Distance is 42 centimeters.
```

IMU values are intentionally not spoken because they would make the announcement too long.

For quick testing, temporarily change:

```python
SPEAK_INTERVAL = 10.0
```

After confirming the speaker works, change it back to 120 seconds.

## Libraries

The sketch uses:

```text
RobotShield 1.0.6
DHT sensor library 1.4.6
Adafruit Unified Sensor 1.1.15
SunFounder_IMU 1.1.2
```

The App uses:

```text
arduino:web_ui
sunfounder_tts
Camera
```

Only the **Espeak** offline TTS engine is used. The STT Brick is not included.
