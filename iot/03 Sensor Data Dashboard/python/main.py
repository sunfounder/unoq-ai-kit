from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI

ui = WebUI()

def update_light_level(value: int):
    light_level = max(0, min(100, int(value)))
    print(f"Light level: {light_level}%", flush=True)
    ui.send_message("light_level", {"value": light_level})

Bridge.provide("update_light_level", update_light_level)

App.run()
