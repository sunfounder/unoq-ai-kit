# 02 Dynamic TTS Weather Reporter

The **Dynamic TTS Weather Reporter** reads temperature and humidity from a DHT11 sensor, turns the live values into a sentence with a Python f-string, and announces the result through the speaker every 30 seconds. Unlike Lesson 1 where the spoken text was fixed, the message here changes every time the sensor readings change.

## Software

### Bricks Used

This example uses the following Bricks:

- `robot_shield` — Provides access to the Robot Shield hardware (I2C, GPIO, audio, PWM)
- `sunfounder_tts` — Local text-to-speech engine (EdgeTTS)

### Libraries Used

- **RobotShield** library (install via Library Manager)
- **SunFounder_TTS** library (install via Library Manager)
- **DHT sensor library** (install via Library Manager)

## Hardware

- Arduino UNO Q ×1
- Multimedia Carrier / Robot Shield with speaker ×1
- DHT11 temperature and humidity sensor module ×1
- Breadboard ×1
- Jumper wires
- USB-C cable ×1

## Wiring

Connect the DHT11 module as follows:

- DHT11 **VCC** → **5V**
- DHT11 **DATA** → **D2**
- DHT11 **GND** → **GND**

![Wiring Diagram](assets/docs_assets/wiring_dht11.png)

> Double-check the labels on your DHT11 module — different boards may arrange pins differently.

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **My Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `02 Dynamic TTS Weather Reporter.zip` from `unoq-ai-kit\media`.
4. Install the **DHT sensor library** if App Lab prompts you.
5. Click **Run**.
6. Every 30 seconds, the speaker announces: *"The temperature is 26.3 degrees Celsius. The humidity is 58.2 percent."* Try breathing warm air onto the DHT11 — the next announcement reflects the change.

## How it Works

```text
DHT11 sensor → sketch reads temp & humidity
    │
    ▼
Bridge.call("read_weather") → returns "26.3,58.2"
    │
    ▼
Python splits into temperature & humidity
    │
    ▼
f-string formats: "The temperature is 26.3 degrees..."
    │
    ▼
tts.say(message) → speaker announces
    │
    ▼
Wait 30 seconds, repeat
```

- The sketch reads the DHT11 and returns both values as a single comma-separated string via Bridge.
- Python splits this string into two numbers, then uses an **f-string** to insert the live values into a natural sentence.
- Because the sensor readings change with the environment, the spoken message also changes — this is the core concept: **changing data → changing speech**.

## Code Overview

### Python

`python/main.py` runs on the Linux MPU.

```python
import time
from arduino.app_utils import Bridge
from sunfounder_tts import EdgeTTS

WEATHER_RPC = "read_weather"
ANNOUNCEMENT_INTERVAL = 30

tts = EdgeTTS(gain=0.4)
tts.set_voice("en-US-JennyNeural")

while True:
    sensor_data = str(Bridge.call(WEATHER_RPC, "")).strip()

    temperature_text, humidity_text = sensor_data.split(",", 1)
    temperature = float(temperature_text)
    humidity = float(humidity_text)

    message = (
        f"The temperature is {temperature:.1f} degrees Celsius. "
        f"The humidity is {humidity:.1f} percent."
    )

    tts.say(message)
    time.sleep(ANNOUNCEMENT_INTERVAL)
```

- ``Bridge.call("read_weather", "")`` — Asks the sketch to read the DHT11. Returns a string like ``"26.3,58.2"``.
- ``sensor_data.split(",", 1)`` — Splits the string at the comma into separate temperature and humidity values.
- **f-string** ``f"... {temperature:.1f} ..."`` — Inserts the current variable value into the sentence. The ``:.1f`` formats it to one decimal place.
- ``tts.say(message)`` — Converts the sentence to speech and plays it through the speaker.

### Sketch

`sketch/sketch.ino` runs on the STM32 MCU.

```cpp
#include "DHT.h"
#include <Arduino_RouterBridge.h>

#define DHTPIN 2
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

String readWeather(String message) {
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();

    if (isnan(humidity) || isnan(temperature)) {
        return "error";
    }

    return String(temperature, 1) + "," + String(humidity, 1);
}

void setup() {
    dht.begin();
    Bridge.begin();
    Bridge.provide("read_weather", readWeather);
}

void loop() { delay(10); }
```

- ``Bridge.provide("read_weather", readWeather)`` — Registers a function that Python can call via Bridge.
- ``dht.readTemperature()`` and ``dht.readHumidity()`` — Read the sensor values.
- The function returns both values as ``"temperature,humidity"`` — a simple format Python can easily parse.

## Troubleshooting

### "Failed to read from the DHT11 sensor"

* **Cause:** The DHT11 is wired incorrectly, or the library is missing.
* **Solution:** Check VCC→5V, DATA→D2, GND→GND. Install the DHT sensor library if prompted.

### No sound from the speaker

* **Cause:** The audio environment isn't configured.
* **Solution:** Run ``./docker-img-make`` in the terminal. Verify the 01 Local TTS lesson works first.
