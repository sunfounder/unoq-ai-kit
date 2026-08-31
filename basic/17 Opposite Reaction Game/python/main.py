import time

from arduino.app_utils import App

print("Opposite Reaction Game is running.")


def loop():
    """Keep the App running while the sketch controls the game."""
    time.sleep(10)


App.run(user_loop=loop)
