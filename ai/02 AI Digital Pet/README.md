# 02 AI Digital Pet

Chat with Pixel, a friendly AI pet. The LLM writes a short reply and chooses an emotion at the same time. The reply appears in the Web UI, while the matching expression appears on the UNO Q 8×13 LED matrix.

## What You'll Learn

- How to ask an LLM for structured JSON output
- How to generate a natural-language reply and a hardware command together
- How Python validates the LLM response before controlling hardware
- How Bridge sends an emotion code to the Arduino sketch
- How `Arduino_LED_Matrix` displays an 8×13 expression

## Hardware Requirements

- Arduino UNO Q ×1
- USB-C cable ×1
- A computer running Arduino App Lab

No external circuit is required. This lesson uses the UNO Q onboard LED matrix.

## How to Use

1. Download [02 AI Digital Pet.zip](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/02.AI.Digital.Pet.zip) and import it in **Arduino App Lab**.
2. Click **Run**. App Lab asks for your OpenAI API Key the first time.
3. Enter the key, save it, and run the App again.
4. When the Web UI opens, type a message and press **Send**.
5. Read Pixel's response in the browser and watch the UNO Q matrix expression change.

Try messages such as:

- `I passed my exam today!`
- `I lost my favorite toy.`
- `I just saw something unbelievable!`
- `Why is the sky blue?`
- `Hello, Pixel!`

## Emotions

| Emotion | When it is used |
|---|---|
| `happy` | Positive, exciting, or friendly messages |
| `sad` | Disappointing or upsetting messages |
| `surprised` | Unexpected or amazing messages |
| `thinking` | Questions or thoughtful messages |
| `neutral` | General messages or safe fallback |

## How It Works

```text
Browser message
      ↓
CloudLLM → OpenAI GPT
      ↓
{"emotion":"happy","reply":"That is wonderful!"}
      ↓
Python validates the JSON
      ├── Web UI displays the reply
      └── Bridge.call("show_emotion", 1)
                    ↓
             UNO Q LED matrix
```

The System Prompt asks the LLM to return only JSON:

```json
{
  "emotion": "happy",
  "reply": "Your short reply here."
}
```

If the LLM returns invalid JSON or an unsupported emotion, Python safely falls back to `neutral`.

## Troubleshooting

### The Web UI says to configure the API Key

Enter a valid OpenAI API key in the CloudLLM brick configuration, save it, and run the App again.

### The matrix stays neutral

Check the Python log for an LLM or Bridge error. A neutral face is also used whenever the LLM response cannot be parsed safely.

### The Web UI does not open

Make sure the App is running and allow the App Lab Web UI window if the browser blocks it.

## Core Concept

**AI can generate a reply and structured data that controls physical hardware at the same time.**
