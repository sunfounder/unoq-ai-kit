# Receives light levels from the sketch and streams them to the web UI.
# Data flow: sketch (photoresistor, A0) -> Python (Bridge) -> browser (WebUI).
#
from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI

# Initialize the web UI.
ui = WebUI()

# Bridge callback: called by the sketch on each sensor sample.
def update_light_level(value: int):
    light_level = max(0, min(100, int(value)))
    print(f"Light level: {light_level}%", flush=True)
    ui.send_message("light_level", {"value": light_level})

# Register the callback so the sketch can call it by name.
Bridge.provide("update_light_level", update_light_level)

# Start the application.
App.run()
