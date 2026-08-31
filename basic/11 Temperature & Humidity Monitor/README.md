# 11 Temperature & Humidity Monitor

Read temperature and humidity from a DHT11 sensor every 2 seconds using a **non-blocking** timer pattern. The DHT11 communicates over a single data wire — one pin carries both temperature and humidity as a series of precisely timed digital pulses. The DHT library decodes this protocol for you.


## Libraries Used

- **DHT sensor library**
- **Adafruit Unified Sensor**


## Hardware

- Pan Tilt Kit ×1
- DHT11 temperature & humidity sensor module ×1
- Jumper wires
- USB-C cable ×1


## Wiring

Connect the DHT11 module to the UNO Q.

![Wiring Diagram](assets/docs_assets/wiring_dht11.png)

## How to Use the Example

1. Open **Arduino App Lab**.
2. Select **Apps** → **Create New App** → **Import App** → **Import from Computer**.
3. Import `11 Temperature & Humidity Monitor.zip` from `unoq-ai-kit\basic`.
4. Click **Run**.
5. Open the **Serial Monitor** to see temperature (°C) and humidity (%) readings every 2 seconds. Try breathing on the sensor — the humidity should spike.

## How it Works

**Flow**

- `setup()` — starts the Serial Monitor and initializes the DHT11 sensor with `dht.begin()`
- `loop()` — checks the non-blocking timer; when 2 seconds have passed, reads and prints temperature and humidity

**The non-blocking timer**

`delay(2000)` would freeze the whole sketch, so `millis()` is checked instead — the code only acts when `currentMillis - lastReadTime` reaches `interval` (2000 ms), leaving the board free to do other work between readings.

**The 2-second interval**

The DHT11 physically can't produce fresh readings faster than about once a second, so the 2000 ms `interval` respects that hardware limit while keeping the sketch responsive.

**Reading the sensor**

The DHT11 sends 40 bits of precisely timed pulses on a single data wire; the DHT library decodes that protocol for you. `dht.readHumidity()` and `dht.readTemperature()` return clean numbers.

**Catching bad readings**

If the sensor is unplugged or a wire is loose, the library returns NaN ("not a number") — the `isnan()` check prints an error message instead of letting garbage values through.

