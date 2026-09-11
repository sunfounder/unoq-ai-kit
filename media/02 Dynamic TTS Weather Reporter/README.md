# 02 Dynamic TTS Weather Reporter

The **Dynamic TTS Weather Reporter** reads temperature and humidity from a DHT11 sensor, turns the live values into a sentence with a Python f-string, and announces the result through the speaker every 30 seconds. Unlike the earlier Local TTS example where the spoken text was fixed, the message here changes every time the sensor readings change.

## Software

### Bricks Used

This example uses the following Bricks:

- `sunfounder_tts` — Local text-to-speech engine (EdgeTTS)

### Libraries Used

- **DHT sensor library**
- **Adafruit Unified Sensor** library

## Hardware

- Pan Tilt Kit ×1
- DHT11 temperature and humidity sensor module ×1
- Breadboard ×1
- Jumper wires
- USB-C cable ×1

## Wiring

Connect the DHT11 module as follows:

- DHT11 **VCC** → **3.3V**
- DHT11 **DATA** → **D4**
- DHT11 **GND** → **GND**

![Wiring Diagram](assets/docs_assets/wiring_dht11.png)

> Double-check the labels on your DHT11 module — different boards may arrange pins differently.

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `02 Dynamic TTS Weather Reporter.zip` from `unoq-ai-kit\media`.
4. Click **Run**.
5. Every 30 seconds, the speaker announces: *"The temperature is 26.3 degrees Celsius. The humidity is 58.2 percent."* Try breathing warm air onto the DHT11 — the next announcement reflects the change.

> **Note:** The first time you run a TTS example on this UNO Q, App Lab needs to download and prepare the TTS runtime and audio dependencies. This may take half an hour or more, depending on your network connection. Keep the UNO Q connected to the Internet and wait for the setup to complete. This setup only happens once — after it finishes, every TTS example starts much faster.

## How it Works

- DHT11 sensor → the sketch reads temperature and humidity
- `Bridge.call("read_weather")` → returns "26.3,58.2"
- Python splits the result into temperature and humidity
- f-string formats the sentence: "The temperature is 26.3 degrees..."
- `tts.say(message)` → the speaker announces
- Wait 30 seconds, then repeat

- The sketch reads the DHT11 and returns both values as a single comma-separated string via Bridge.
- Python splits this string into two numbers, then uses an **f-string** to insert the live values into a natural sentence.
- Because the sensor readings change with the environment, the spoken message also changes — this is the core concept: **changing data → changing speech**.
