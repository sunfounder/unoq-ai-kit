# SPDX-FileCopyrightText: Copyright (C) SunFounder
# SPDX-License-Identifier: MIT

"""Local STT basic example.

The program automatically records a short audio clip, transcribes it locally,
and prints the recognized text in the App Lab Output window.

"""

import threading
import time

from arduino.app_utils import App

from sunfounder_stt import STT


# Recording duration for each listening cycle, in seconds.
LISTEN_SECONDS = 5


def stt_worker():
    """Continuously record short clips and transcribe them locally."""
    try:
        print("Preparing the audio input...", flush=True)
        

        print("Loading the local STT model...", flush=True)
        stt = STT(type="local_fast", language="en")

        print("Local STT is ready.", flush=True)
        print(f"The microphone will listen for {LISTEN_SECONDS} seconds each time.", flush=True)

        while True:
            try:
                stt.reset()

                print("\nListening... Please speak.", flush=True)
                stt.start_listening()
                time.sleep(LISTEN_SECONDS)
                stt.stop_listening()

                print("Recognizing locally...", flush=True)
                text = stt.get_result(timeout=60)
                if isinstance(text, dict):
                    text = text.get("text", "")
                text = text.strip() if text else ""

                if text:
                    print(f"You said: {text}", flush=True)
                else:
                    print("No speech detected.", flush=True)

                time.sleep(1)

            except Exception as error:
                print(f"STT cycle error: {error}", flush=True)
                try:
                    stt.stop_listening()
                except Exception:
                    pass
                time.sleep(2)

    except Exception as error:
        print(f"Local STT initialization failed: {error}", flush=True)


threading.Thread(target=stt_worker, daemon=True).start()

print("Local STT demo started.", flush=True)
App.run()
