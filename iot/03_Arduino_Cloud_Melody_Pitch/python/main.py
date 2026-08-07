from arduino.app_bricks.arduino_cloud import ArduinoCloud
from arduino.app_utils import App, Bridge


iot_cloud = ArduinoCloud()


def pitch_callback(client: object, value: int):
    """Update the melody pitch from the Arduino Cloud slider."""

    pitch_level = max(0, min(50, int(value)))

    print(f"Pitch level: {pitch_level}", flush=True)

    Bridge.call("set_pitch_level", pitch_level)


iot_cloud.register(
    "pitch",
    value=25,
    on_write=pitch_callback,
)

App.run()