# 12 IoT Smart Room

A final IoT project that combines sensing, automation, control, camera monitoring, and voice interaction.

![Result](assets/docs_assets/smart_room_result.png)

## Smart Room Systems

- **Environment** — DHT11 measures temperature and humidity; a photoresistor on A0 measures ambient light.
- **Ventilation** — D0/D1 motor acts as a fan. AUTO mode turns it on at 28°C; MANUAL mode uses the Web UI.
- **Security** — PIR motion detection and a live CSI security camera.
- **Camera Control** — Joystick A3/A2 controls D9/D10 pan-tilt servos.
- **Smart Lighting** — RGB LED on D6/D7/D8. Choose any color from the Web UI color wheel or use voice color commands.
- **Voice Assistant** — Local STT controls the room; TTS confirms actions and speaks system status.

## Wiring

| Module | UNO Q |
| --- | --- |
| Motor IN1 | D0 |
| Motor IN2 | D1 |
| PIR | D4 |
| DHT11 | D5 |
| RGB LED R | D6 |
| RGB LED G | D7 |
| RGB LED B | D8 |
| Pan Servo | D9 |
| Tilt Servo | D10 |
| Photoresistor | A0 |
| Joystick X | A3 |
| Joystick Y | A2 |
| Camera | CSI |

The ultrasonic sensor is not used in this final project.

## Voice Commands

- `Fan on` / `Fan off`
- `Light on` / `Light off`
- `Set light red`
- `Set light green`
- `Set light blue`
- `Set light yellow`
- `Set light purple`
- `Set light cyan`
- `Set light white`
- `Set light orange`
- `Set light pink`
- `Look left` / `Look right`
- `Look up` / `Look down`
- `Center`
- `System status`

## Servo Range

- Left: 135°
- Right: 45°
- Up: 45°
- Down: 115°
- Center: 90°
