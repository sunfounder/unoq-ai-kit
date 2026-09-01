# SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
#
# SPDX-License-Identifier: MPL-2.0

# Web app that controls an RGB LED through the sketch.
# Data flow: browser -> Python (WebUI) -> sketch (Bridge, RobotShield PWM).
#
from arduino.app_utils import *
from arduino.app_bricks.web_ui import WebUI

# Current RGB color state
rgb_color = {"r": 0, "g": 0, "b": 0}


def get_rgb_status():
    """Return current RGB color for the web UI."""
    return {
        "r": rgb_color["r"],
        "g": rgb_color["g"],
        "b": rgb_color["b"],
    }


def handle_set_rgb_color(client, data):
    """Receive RGB values from the web UI and send to sketch."""
    global rgb_color

    r = int(data.get("r", 0))
    g = int(data.get("g", 0))
    b = int(data.get("b", 0))

    rgb_color = {"r": r, "g": g, "b": b}

    # Call the sketch function via Bridge RPC
    Bridge.call("set_rgb_color", r, g, b)

    # Broadcast new color to all connected clients
    ui.send_message("rgb_status_update", get_rgb_status())


def handle_get_initial_state(client, data):
    """Send current color to newly connected client."""
    ui.send_message("rgb_status_update", get_rgb_status(), client)


# Initialize WebUI
ui = WebUI()

# Register socket message handlers
ui.on_message("set_rgb_color", handle_set_rgb_color)
ui.on_message("get_initial_state", handle_get_initial_state)

# Start the application
App.run()
