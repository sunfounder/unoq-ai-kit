# Cloud app that adjusts the melody pitch played by the sketch.
# Data flow: Arduino Cloud slider -> Python (ArduinoCloud) -> sketch (Bridge).
#
from arduino.app_bricks.arduino_cloud import ArduinoCloud
from arduino.app_utils import App, Bridge


# Connect to Arduino Cloud.
iot_cloud = ArduinoCloud()


def pitch_callback(client: object, value: int):
    """Update the melody pitch from the Arduino Cloud slider."""

    # Clamp the cloud value to the 0-50 pitch range.
    pitch_level = max(0, min(50, int(value)))

    print(f"Pitch level: {pitch_level}", flush=True)

    Bridge.call("set_pitch_level", pitch_level)


# Register the cloud variable; 25 is the default pitch level.
iot_cloud.register(
    "pitch",
    value=25,
    on_write=pitch_callback,
)

# Start the application.
App.run()