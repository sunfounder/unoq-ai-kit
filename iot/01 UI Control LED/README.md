# 01 UI Control LED

Control an external LED from a web page. The browser sends button clicks through Socket.IO to the Python backend, Python calls the sketch through Bridge, and the sketch toggles the LED on digital pin D5.

## Software

### Bricks Used

- `web_ui` — Creates the web interface and provides real-time communication between the browser and the Python backend

## Hardware

- Arduino UNO Q ×1
- Breadboard ×1
- Red LED ×1
- 220 Ω resistor ×1
- Jumper wires
- USB-C cable ×1

## Wiring

Connect the LED through a 220 Ω resistor between digital pin D5 and GND.

![Wiring Diagram](assets/docs_assets/wiring_led.png)

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `01 UI Control LED.zip` from `unoq-ai-kit\iot`.
4. Click **Run**.
5. When the Web UI opens, click the **LED IS OFF** button to toggle the LED.

## How it Works

**Flow**

- Browser — sends `toggle_led` events through Socket.IO when the button is clicked
- Python (`main.py`) — receives the event, calls `Bridge.call("set_led_state", led_is_on)`, then broadcasts the new state back to the browser
- Sketch (`sketch.ino`) — `Bridge.provide("set_led_state", set_led_state)` registers the function that Python calls; `digitalWrite(ledPin, ...)` sets pin D5
- The sketch's `loop()` is empty — everything is event-driven through Bridge

**The bridge pattern**

The browser never talks to the sketch directly. Each click travels: browser → Python → Bridge → sketch → LED. Python keeps a `led_is_on` flag so the UI always shows the current state, even if multiple browsers are connected.

**The sketch side**

`set_led_state(bool state)` receives the desired state from Python and calls `digitalWrite(ledPin, state ? HIGH : LOW)`. That's the entire hardware logic — one pin, one function.
