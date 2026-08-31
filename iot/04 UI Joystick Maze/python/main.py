from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI

ui = WebUI()


def joystick_move(direction: str):
    """Receive a direction from the sketch and forward it to the web game."""
    direction = str(direction).lower()

    if direction in ("up", "down", "left", "right"):
        ui.send_message("joystick_move", {"direction": direction})


def reset_game():
    """Reset the maze when the joystick button is pressed."""
    ui.send_message("reset_game", {})


Bridge.provide("joystick_move", joystick_move)
Bridge.provide("reset_game", reset_game)

App.run()
