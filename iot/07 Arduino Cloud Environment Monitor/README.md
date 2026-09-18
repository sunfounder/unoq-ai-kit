# 07 Arduino Cloud Environment Monitor

Build an IoT environment monitoring system using Arduino Cloud. The sketch reads temperature and humidity from a DHT11 sensor every 5 seconds and uploads them to the Cloud, while a switch on the Cloud Dashboard remotely controls an external LED on D5 — Cloud monitoring and Cloud control in one project.

## Software

### Bricks Used

- `arduino_cloud` — Connects the App to Arduino Cloud; registers the `temperature`, `humidity`, and `led` variables

## Hardware

- Pan Tilt Kit ×1
- Breadboard ×1
- DHT11 temperature and humidity sensor module ×1
- LED ×1
- 220 Ω resistor ×1
- Jumper wires
- USB-C cable ×1

## Wiring

Connect the DHT11's VCC to 3.3V, DATA to D4, and GND to GND; connect the external LED's anode to D5 and its cathode through a 220 Ω resistor to GND.

![Wiring Diagram](assets/docs_assets/wiring_dht11.png)

## How to Use the Example

1. Download [`07 Arduino Cloud Environment Monitor.zip`](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/07.Arduino.Cloud.Environment.Monitor.zip).
2. In App Lab, go to **Apps** → **Create New App** → **Import App** → **Import from Computer** and open the package you downloaded.
3. Open the **Arduino Cloud** Brick, click **Brick Configuration**, and enter your `ARDUINO_DEVICE_ID` and `ARDUINO_SECRET`.
4. In Arduino Cloud, create a Thing associated with your Device, with three variables: `temperature` and `humidity` (Floating Point Number, Read Only, On change) and `led` (Boolean, Read & Write, On change). Build a Dashboard with widgets linked to all three.
5. Click **Run**.
6. Open the Dashboard — temperature and humidity widgets update with each DHT11 reading, and the LED switch turns the external LED on or off.

## How it Works

**Flow**

- Sketch (`sketch.ino`) — reads the DHT11 every 5 seconds (`SENSOR_INTERVAL = 5000`) with a non-blocking `millis()` timer, then calls `Bridge.notify("update_environment_cloud", temperature, humidity)`. It also provides `set_led_state()` for Python to call.
- Python (`main.py`) — `Bridge.provide("update_environment_cloud", ...)` receives the readings and writes them to the Cloud (`iot_cloud.temperature`, `iot_cloud.humidity`). When the Cloud switch changes, `led_callback()` calls `Bridge.call("set_led_state", bool(value))`.
- Arduino Cloud — the Dashboard widgets display the uploaded values; the switch writes to the `led` variable.

**The five-second interval**

The DHT11 is relatively slow, so a 5-second interval avoids sending unnecessary Cloud updates and respects the sensor's hardware limits. The `millis()` timer keeps the sketch responsive between readings.

**Two directions on one bridge**

This project is the first with bidirectional Cloud traffic: sensor data flows **up** (sketch → Python → Cloud), while the LED command flows **down** (Cloud → Python → sketch). The same Bridge carries both.
