import time

from arduino.app_utils import App

print("This example uses the Arduino sketch to display patterns on the LED matrix.")


def loop():
    """Keep the App running while the sketch controls the LED matrix."""
    time.sleep(10)


App.run(user_loop=loop)
