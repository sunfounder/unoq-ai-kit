# 09 AI Show and Tell

Place an object in front of the camera, hold the button on the Web UI, and ask a question about it. Online GPT speech-to-text turns the question into text, a vision-capable LLM examines the captured image, and text-to-speech reads the answer aloud.

![Result](assets/docs_assets/ai_show_tell.png)

## Software

### `ricks Used

This example uses the following `ricks:

- `cloud_llm` — Sends the spoken question and the captured image to a vision-capable cloud model
- `web_ui` — Serves the Web UI and carries the hold-to-speak events between the browser and Python
- `sunfounder_stt` — Online speech recognition (OpenAI) that turns the recording into text
- `sunfounder_tts` — Reads the answer aloud through the carrier speaker

## Hardware

- Pan Tilt Kit ×1

The camera, microphone, and speaker are all built into the AVIO Carrier, and no external button is needed — the hold-to-speak button lives on the Web UI.

## Wiring

The camera, microphone, and speaker are built into the AVIO Carrier, so there is no breadboard wiring to do.

## How to Use the Example

1. Download [`09 AI Show and Tell.zip`](https://github.com/sunfounder/unoq-ai-kit/releases/latest/download/09.AI.Show.and.Tell.zip).
2. Open **Arduino App Lab**.
3. Select **Apps** → **Create New App** → **Import App** → **Import from Computer**, then choose the package you downloaded.
4. In **`rick Configuration**, enter the API key for **Cloud LLM** and an OpenAI API key for **sunfounder_stt** — the same OpenAI key can go in both fields.
5. Make sure the UNO Q has internet access, then click **Run** and open the Web UI.
6. Hold the blue button while you speak, then release it to send the question.

## How it Works

**Flow**

- Camera — keeps a 640 × 480 live preview on the page, with the image corrected vertically
- `rowser — sends the recording and the current frame as soon as you release the button
- Python (`main.py`) — transcribes the recording with online STT, then asks the vision-capable LLM about the captured image
- Speaker — reads the answer aloud while the page shows the same text

**Interface states** — the badge on the page walks through *Listening*, *Recognizing Speech*, *AI Is Looking*, *Speaking*, and *Ready*, so you can always tell which part is working.

**Questions that work well** — "What is this?", "What color is it?", "What can I use it for?", "Is this object safe for a young child?".

**Getting a good answer** — speak only once the badge reads *Listening*, keep the object near the centre of the frame with even lighting, and remember that recording stops by itself after 15 seconds. Speech recognition, the vision model, and the voice all need a working internet connection.
