# 03 AI Environment Advisor

Read temperature, humidity, and light data from the real world, then ask an LLM to explain the current environment and provide a practical suggestion.

## What You'll Learn

- How Arduino sends live sensor readings to Python with `Bridge.notify()`
- How to include real-world data in an LLM prompt
- How to request structured JSON analysis from an LLM
- Why live sensor updates and LLM requests should run at different rates
- How to show live measurements and AI analysis in one Web UI

## Hardware Requirements

- Arduino UNO Q ×1
- Robot Shield ×1
- DHT11 temperature and humidity sensor ×1
- Photoresistor module ×1
- USB-C cable ×1
- Jumper wires

## Wiring

| Component | Robot Shield |
|---|---|
| DHT11 signal | D4 |
| DHT11 VCC | 5V |
| DHT11 GND | GND |
| Photoresistor signal | A0 |
| Photoresistor VCC | 5V |
| Photoresistor GND | GND |

## How to Use

1. Connect the DHT11 to D4 and the photoresistor module to A0.
2. Import `03 AI Environment Advisor.zip` into Arduino App Lab.
3. Click **Run**. Enter your OpenAI API key when App Lab asks for it.
4. Wait for temperature, humidity, and light data to appear in the Web UI.
5. Click **Analyze Environment**.
6. Read the AI status, summary, and suggestion.

The sensors update every two seconds. The LLM is called only when you click the analysis button, so live monitoring does not continuously consume API requests.

## How It Works

```text
DHT11 + Photoresistor
          ↓
Arduino reads sensors every 2 seconds
          ↓ Bridge.notify()
Python stores the latest readings
          ↓
Web UI displays live data
          ↓ User clicks Analyze
CloudLLM analyzes one snapshot
          ↓
Status + Summary + Suggestion
```

The LLM returns JSON such as:

```json
{
  "status": "Warm",
  "summary": "The room is warmer than a typical comfortable range.",
  "suggestion": "Open a window or improve air circulation."
}
```

## Light-Level Note

The displayed light percentage is a relative classroom measurement calculated from the A0 reading. If your photoresistor module is electrically reversed and the percentage decreases under brighter light, change this line in `python/main.py`:

```python
percent = round(raw * 100 / 1023)
```

to:

```python
percent = round((1023 - raw) * 100 / 1023)
```

## Troubleshooting

### Temperature and humidity remain blank

Check the DHT11 signal, 5V, and GND connections. The app does not send invalid DHT11 readings to the LLM.

### Light percentage moves in the wrong direction

Use the inverted calculation described in the Light-Level Note.

### The analysis asks for an API key

Configure a valid OpenAI API key in the CloudLLM brick, save it, and run the App again.

## Core Concept

**An LLM can turn raw sensor measurements into a clear explanation and a practical recommendation.**
