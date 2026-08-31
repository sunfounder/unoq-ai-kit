"""
IoT Control Center

Local dashboard features:
- CSI camera live preview
- DHT11 temperature / humidity
- PIR motion status
- ultrasonic distance
- 10-axis IMU data
- physical joystick position and pan/tilt angles
- System Run switch
- Motor M0 switch (30% power)
- offline speaker status announcement every 2 minutes

No STT, Arduino Cloud, Telegram, Edge AI, or external Internet service is used.
"""

import base64
import time
from pathlib import Path

import cv2

from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_peripherals.camera import Camera
from sunfounder_tts import Espeak


ui = WebUI()

STREAM_INTERVAL = 0.25       # About 4 FPS
JPEG_QUALITY = 65

SPEAK_INTERVAL = 120.0       # 2 minutes

AUDIO_OUTPUT_DIR = Path("/app/audio_output")
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

latest_environment = {
    "temperature": None,
    "humidity": None,
    "pir": False,
    "distance": None,
}

latest_joystick = {
    "x": 512,
    "y": 512,
    "pan": 0,
    "tilt": 0,
}

latest_imu = {
    "accel": [0, 0, 0],
    "gyro": [0, 0, 0],
    "mag": [0, 0, 0],
    "azimuth": 0,
    "pressure": 0,
    "altitude": 0,
    "imu_temperature": 0,
}

system_running = True
motor_enabled = False

print("Initializing camera...", flush=True)

camera = Camera()
camera.start()
time.sleep(1)

print("Camera ready.", flush=True)

print("Initializing offline speaker...", flush=True)

tts = Espeak()
tts.set_amp(110)
tts.set_speed(150)
tts.set_gap(3)
tts.set_pitch(48)

print("Speaker ready.", flush=True)


def send_camera_frame(frame):
    """Encode one frame as JPEG and send it to the local Web UI."""
    success, encoded = cv2.imencode(
        ".jpg",
        frame,
        [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY],
    )

    if not success:
        return

    image_base64 = base64.b64encode(
        encoded.tobytes()
    ).decode("ascii")

    ui.send_message(
        "camera_frame",
        {"image": image_base64},
    )


def environment_update(temperature, humidity, pir, distance):
    """Receive DHT11, PIR, and ultrasonic values from the sketch."""
    latest_environment["temperature"] = float(temperature)
    latest_environment["humidity"] = float(humidity)
    latest_environment["pir"] = bool(pir)
    latest_environment["distance"] = float(distance)

    ui.send_message(
        "environment_update",
        latest_environment,
    )


def joystick_update(x, y, pan, tilt):
    """Receive physical joystick and pan/tilt state from the sketch."""
    latest_joystick["x"] = int(x)
    latest_joystick["y"] = int(y)
    latest_joystick["pan"] = int(pan)
    latest_joystick["tilt"] = int(tilt)

    ui.send_message(
        "joystick_update",
        latest_joystick,
    )


def imu_update(
    ax, ay, az,
    gx, gy, gz,
    mx, my, mz,
    azimuth,
    pressure,
    altitude,
    imu_temperature,
):
    """Receive the 10-Axis IMU data from the sketch."""
    latest_imu["accel"] = [
        float(ax),
        float(ay),
        float(az),
    ]

    latest_imu["gyro"] = [
        float(gx),
        float(gy),
        float(gz),
    ]

    latest_imu["mag"] = [
        float(mx),
        float(my),
        float(mz),
    ]

    latest_imu["azimuth"] = float(azimuth)
    latest_imu["pressure"] = float(pressure)
    latest_imu["altitude"] = float(altitude)
    latest_imu["imu_temperature"] = float(imu_temperature)

    ui.send_message(
        "imu_update",
        latest_imu,
    )


Bridge.provide("environment_update", environment_update)
Bridge.provide("joystick_update", joystick_update)
Bridge.provide("imu_update", imu_update)


def send_control_state(client=None):
    data = {
        "system_running": system_running,
        "motor_enabled": motor_enabled,
        "motor_power": 30,
    }

    if client is None:
        ui.send_message("control_state", data)
    else:
        ui.send_message("control_state", data, client)


def on_toggle_system(client, data):
    """Enable or disable actuator operation."""
    global system_running

    system_running = bool(data.get("enabled", False))

    Bridge.call(
        "set_system_running",
        system_running,
    )

    if not system_running:
        # Motor is physically stopped by the sketch.
        # Preserve the user's Motor switch preference for the next RUN.
        pass

    send_control_state()


def on_toggle_motor(client, data):
    """Turn M0 on/off. ON always means 30% power."""
    global motor_enabled

    motor_enabled = bool(data.get("enabled", False))

    Bridge.call(
        "set_motor_enabled",
        motor_enabled,
    )

    send_control_state()


def on_get_initial_state(client, data):
    ui.send_message(
        "environment_update",
        latest_environment,
        client,
    )

    ui.send_message(
        "joystick_update",
        latest_joystick,
        client,
    )

    ui.send_message(
        "imu_update",
        latest_imu,
        client,
    )

    send_control_state(client)


ui.on_message("toggle_system", on_toggle_system)
ui.on_message("toggle_motor", on_toggle_motor)
ui.on_message("get_initial_state", on_get_initial_state)


def build_status_message():
    """Build a short spoken system summary."""
    temperature = latest_environment["temperature"]
    humidity = latest_environment["humidity"]
    distance = latest_environment["distance"]
    pir = latest_environment["pir"]

    if temperature is None or humidity is None:
        return "System is running. Environmental data is not ready yet."

    if distance is None or distance < 0:
        distance_text = "Distance is out of range."
    else:
        distance_text = (
            f"Distance is {round(distance)} centimeters."
        )

    motion_text = (
        "Motion is detected."
        if pir
        else "No motion is detected."
    )

    return (
        "System status. "
        f"Temperature is {round(temperature)} degrees Celsius. "
        f"Humidity is {round(humidity)} percent. "
        f"{motion_text} "
        f"{distance_text}"
    )


last_stream_time = 0.0
last_speak_time = time.monotonic()


def loop():
    """Run camera streaming and periodic offline status announcements."""
    global last_stream_time
    global last_speak_time

    now = time.monotonic()

    if now - last_stream_time >= STREAM_INTERVAL:
        frame = camera.capture()

        # Correct orientation on the pan-tilt mount.
        frame = cv2.flip(frame, 0)

        send_camera_frame(frame)
        last_stream_time = now

    if now - last_speak_time >= SPEAK_INTERVAL:
        message = build_status_message()

        print(f"Speaker: {message}", flush=True)

        try:
            tts.say(message)
        except Exception as exc:
            # Do not stop the whole IoT project if audio playback fails.
            print(
                f"Speaker error: {exc}",
                flush=True,
            )

        last_speak_time = time.monotonic()

    time.sleep(0.02)


print("=== IoT Control Center ===", flush=True)
print("Open the local Web UI to monitor and control the system.", flush=True)
print("Offline status announcement interval: 2 minutes.", flush=True)

try:
    App.run(user_loop=loop)
finally:
    try:
        Bridge.call("set_system_running", False)
    except Exception:
        pass

    camera.stop()
