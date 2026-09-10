# SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
#
# SPDX-License-Identifier: MPL-2.0

"""
Certification Test — verify every peripheral on the UNO Q.

Runs an automatic test sequence and prints PASS / FAIL / CHECK for
each peripheral:

  1. IMU          (automatic — reads accelerometer and gyroscope)
  2. PIR          (wave your hand in front of it within 10 seconds)
  3. Ultrasonic   (automatic — reads distance)
  4. DHT11        (automatic — reads temperature and humidity)
  5. Joystick     (move the stick, then press it down)
  6. Servos       (CHECK — pan and tilt sweep, confirm visually)
  7. Motor        (CHECK — forward 2 s, reverse 2 s, stop)
  8. Speaker      (CHECK — plays "Speaker test")
  9. Camera       (automatic — captures and saves a photo)

The summary at the end counts every result.
"""

import os
import time
from pathlib import Path

import cv2

from arduino.app_utils import App, Bridge
from arduino.app_peripherals.camera import Camera
from sunfounder_tts import EdgeTTS


results = []


def report(name, status, detail=""):
    """Print one test result and record it for the summary."""
    results.append(status)
    line = f"[{len(results)}/9] {name:<14} {status:<7}"
    if detail:
        line += f" {detail}"
    print(line, flush=True)


def test_imu():
    """Read the IMU and check the values are not all zero."""
    data = str(Bridge.call("read_imu", "")).strip()

    if data == "error":
        report("IMU", "FAIL", "imu.begin() failed")
        return

    try:
        ax, ay, az, gx, gy, gz = (float(v) for v in data.split(","))
    except (TypeError, ValueError):
        report("IMU", "FAIL", f"unexpected data: {data}")
        return

    if az < 5.0:
        report("IMU", "FAIL", f"accel z too small: {az}")
    else:
        report("IMU", "PASS", f"ax={ax} ay={ay} az={az}")


def test_pir():
    """Wait up to 10 seconds for motion in front of the PIR."""
    print("      wave your hand in front of the PIR sensor...", flush=True)

    deadline = time.monotonic() + 10.0

    while time.monotonic() < deadline:
        if int(Bridge.call("read_pir", "")) == 1:
            report("PIR", "PASS", "motion detected")
            return
        time.sleep(0.1)

    report("PIR", "FAIL", "no motion in 10 s")


def test_ultrasonic():
    """Read the distance and check it is in a sane range."""
    samples = []

    for _ in range(3):
        distance = float(Bridge.call("read_distance", ""))
        samples.append(distance)
        time.sleep(0.1)

    average = sum(samples) / len(samples)

    if 2.0 <= average <= 400.0:
        report("Ultrasonic", "PASS", f"{average:.1f} cm")
    else:
        report("Ultrasonic", "FAIL", f"{average:.1f} cm (out of range)")


def test_dht11():
    """Read temperature and humidity and check the ranges."""
    # Read twice — the first DHT11 read can fail while it stabilizes.
    data = "error"

    for _ in range(3):
        data = str(Bridge.call("read_dht", "")).strip()

        if data != "error":
            break

        time.sleep(1.0)

    if data == "error":
        report("DHT11", "FAIL", "sensor did not respond")
        return

    try:
        temperature_text, humidity_text = data.split(",")
        temperature = float(temperature_text)
        humidity = float(humidity_text)
    except (TypeError, ValueError):
        report("DHT11", "FAIL", f"unexpected data: {data}")
        return

    if 5.0 <= temperature <= 45.0 and 10.0 <= humidity <= 95.0:
        report(
            "DHT11",
            "PASS",
            f"{temperature:.1f} °C, {humidity:.1f} %",
        )
    else:
        report(
            "DHT11",
            "FAIL",
            f"{temperature:.1f} °C, {humidity:.1f} % (out of range)",
        )


def test_joystick():
    """Read the axes, then wait for the stick button."""
    print("      move the stick, then press it down...", flush=True)

    deadline = time.monotonic() + 10.0
    saw_x_motion = False
    saw_y_motion = False
    saw_sw_press = False

    first_x = None
    first_y = None

    while time.monotonic() < deadline:
        data = str(Bridge.call("read_joystick", "")).strip()

        try:
            x_text, y_text, sw_text = data.split(",")
            x, y = int(x_text), int(y_text)
        except ValueError:
            continue

        if first_x is None:
            first_x, first_y = x, y

        if abs(x - first_x) > 80:
            saw_x_motion = True
        if abs(y - first_y) > 80:
            saw_y_motion = True
        if sw_text == "1":
            saw_sw_press = True

        time.sleep(0.1)

    if saw_x_motion and saw_y_motion and saw_sw_press:
        report("Joystick", "PASS", "axes + button OK")
    else:
        detail = []
        if not saw_x_motion:
            detail.append("X axis not moved")
        if not saw_y_motion:
            detail.append("Y axis not moved")
        if not saw_sw_press:
            detail.append("button not pressed")
        report("Joystick", "FAIL", "; ".join(detail))


def test_servos():
    """Sweep both servos — operator confirms visually."""
    print("      pan sweeps 45 -> 135, tilt sweeps 45 -> 115...", flush=True)

    for angle in range(45, 136, 10):
        Bridge.call("set_pan", angle)
        time.sleep(0.08)
    for angle in range(45, 116, 10):
        Bridge.call("set_tilt", angle)
        time.sleep(0.08)

    Bridge.call("set_pan", 90)
    Bridge.call("set_tilt", 90)

    report("Servos", "CHECK", "confirm both moved and returned to center")


def test_motor():
    """Run the motor forward and reverse — operator confirms visually."""
    print("      motor forward 2 s, reverse 2 s, stop...", flush=True)

    Bridge.call("set_motor", 200)
    time.sleep(2.0)

    Bridge.call("set_motor", -200)
    time.sleep(2.0)

    Bridge.call("set_motor", 0)

    report("Motor", "CHECK", "confirm the motor spun both ways")


def test_speaker():
    """Play a short TTS message — operator confirms by listening."""
    print("      playing 'Speaker test one two three.'...", flush=True)

    try:
        os.makedirs("./audio_output", exist_ok=True)
        os.makedirs("/app/audio_output", exist_ok=True)

        tts = EdgeTTS(gain=0.5)
        tts.set_voice("en-US-JennyNeural")
        tts.say("Speaker test one two three.")
    except Exception as error:
        report("Speaker", "FAIL", f"{type(error).__name__}: {error}")
        return

    report("Speaker", "CHECK", "confirm you heard the sentence")


def test_camera():
    """Capture a photo and check it was written."""
    photo_dir = Path("/app/photos")
    photo_dir.mkdir(parents=True, exist_ok=True)

    photo_path = photo_dir / "certification_test.jpg"

    camera = Camera()
    camera.start()
    time.sleep(1)

    frame = camera.capture()
    frame = cv2.flip(frame, 0)

    if frame is None:
        report("Camera", "FAIL", "capture returned no frame")
        return

    if cv2.imwrite(str(photo_path), frame):
        size_kb = photo_path.stat().st_size / 1024
        report("Camera", "PASS", f"photo saved ({size_kb:.0f} KB)")
    else:
        report("Camera", "FAIL", "cv2.imwrite failed")

    camera.stop()


def summary():
    """Print the final tally."""
    passed = results.count("PASS")
    failed = results.count("FAIL")
    checked = results.count("CHECK")

    print("=" * 46, flush=True)
    print(
        f"Summary: {passed} PASS, {failed} FAIL, {checked} CHECK "
        f"({len(results)}/9 tests)",
        flush=True,
    )


def run_tests():
    """Run the whole certification sequence once."""
    print("=== Certification Test ===", flush=True)

    test_imu()
    test_pir()
    test_ultrasonic()
    test_dht11()
    test_joystick()
    test_servos()
    test_motor()
    test_speaker()
    test_camera()

    summary()


def loop():
    time.sleep(10)


run_tests()
App.run(user_loop=loop)
