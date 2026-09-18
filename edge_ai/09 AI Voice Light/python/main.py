"""AI Voice Light: Edge AI keyword spotting.

Behaviour
---------
The keyword spotting model classifies one second of microphone audio at a
time into ``background``, ``hey_arduino`` or ``other``. When the
``hey_arduino`` score clears CONFIDENCE the assistant wakes: it answers
"I'm here.", records one spoken command, prints what it heard, changes the
RGB LED, then goes back to waiting.

Seeing what the model thinks
----------------------------
The brick stays completely silent when a window does not clear the threshold,
which makes a working app look broken. Debug logging for the audio module is
switched on below, exactly as Arduino's own support guidance describes. With
it on, the library prints the winning class and its confidence for the windows
it evaluates:

    Keyword 'background' detected with confidence 100.00%.
    Keyword 'other' detected with confidence 99.11%.
    Keyword 'hey_arduino' detected with confidence 99.97%.

If you only ever see 'background' while you say the wake word, the model does
not match your pronunciation. Raise or lower CONFIDENCE, or train your own
model on Edge Impulse with your own recordings - the model shipped with the
board was trained on a single speaker's voice.

The app reads those same lines back with a logging handler and prints a summary
on every heartbeat, so the verdict is visible without scrolling:

    [HEARD] background 11x (best 100%), other 3x (best 88%)
             Speech was heard, but none of it matched the wake word.

Do NOT wrap KeywordSpotting.infer_from_features to read the raw scores. That
stops the brick's inference loop from running at all (observed: zero windows
evaluated, microphone never opened), and running two KeywordSpotting instances
to get a second threshold does the same thing. Debug logging is the supported
route.
"""

import logging
import re
import subprocess
import threading
import time

# Enable the audio module's debug output. This is the documented way to see
# per-window results, and unlike wrapping the model it does not disturb it.
from arduino.app_internal.core.audio import logger as _audio_logger

# The per-window lines are logger.debug() calls, and the platform's Logger
# defaults to INFO, so they stay invisible until this level is lowered. This
# object is the one the brick actually logs on.
_audio_logger.setLevel(logging.DEBUG)

from arduino.app_utils import App, Bridge
from arduino.app_bricks.keyword_spotting import KeywordSpotting

# The two SunFounder bricks are separate services, and they are the only parts
# of this app that can be missing: the wake word and the light need neither.
# A missing brick is reported and the app keeps running instead of dying at
# import, which is what made the whole lesson look broken.
try:
    from sunfounder_stt import STT
except Exception as _error:
    STT = None
    print(f"[WARN] Speech recognition brick unavailable: {_error}", flush=True)

try:
    from sunfounder_tts import EdgeTTS
except Exception as _error:
    EdgeTTS = None
    print(f"[WARN] Text to speech brick unavailable: {_error}", flush=True)


# How sure the model has to be before the assistant wakes up. The brick's own
# default is 0.8. Lower it (0.3 - 0.5) if your pronunciation scores low; raise
# it if the assistant starts waking on its own.
CONFIDENCE = 0.45

# How often to prove that detection is still alive.
HEARTBEAT_SECONDS = 15.0

# How long to record the spoken command once awake.
COMMAND_SECONDS = 4.0

# How long the startup microphone check listens for.
MIC_CHECK_SECONDS = 1.5

# Bench aids. Set BENCH_WAKE_AFTER_SECONDS to a positive number to run one wake
# cycle that many seconds after startup without saying the wake word; set
# BENCH_COMMAND as well to act on a fixed sentence instead of recording one.
# Both stay off in normal use. They exist because the wake word depends on the
# shipped model matching your voice, while the light, speech and recognition
# halves of the app can be checked without it.
BENCH_WAKE_AFTER_SECONDS = 0.0
BENCH_COMMAND = ""

WAKE_WORD = "hey_arduino"
WAKE_LABEL = "Hey Arduino"

COLOR_PRESETS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "purple": (160, 32, 240),
    "white": (255, 255, 255),
}


class WindowCounter(logging.Handler):
    """Count the model's verdicts by reading the audio module's log lines.

    The library logs one line for every window it evaluates, in the form
    ``Keyword 'background' detected with confidence 100.00%.``. Counting those
    lines turns "nothing happens" into either "it heard only background" or
    "it heard speech but not the wake word", which are two very different
    problems. This only observes log records - the model itself is untouched,
    which matters because wrapping the model stops it from running at all.
    """

    LINE = re.compile(r"Keyword '([^']+)'")
    SCORE = re.compile(r"([0-9]+(?:\.[0-9]+)?)")

    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self._counts = {}
        self._best = {}
        self._lock = threading.Lock()

    def emit(self, record):
        try:
            match = self.LINE.search(record.getMessage())
            if not match:
                return
            label = match.group(1)
            # The confidence is read from the same line but does not have to
            # be there: a label is still worth counting if the wording around
            # it ever changes.
            score = self.SCORE.search(record.getMessage())
            confidence = float(score.group(1)) if score else 0.0
        except Exception:
            return
        with self._lock:
            self._counts[label] = self._counts.get(label, 0) + 1
            self._best[label] = max(self._best.get(label, 0.0), confidence)

    def take(self):
        """Return what has been counted since the last call, then start over."""
        with self._lock:
            counts, best = self._counts, self._best
            self._counts, self._best = {}, {}
        return counts, best


windows = WindowCounter()
# The handler goes on the audio module's own logger, not on the root logger:
# that Logger is created directly as Logger("AudioDetector"), so it is never
# registered with the logging manager, has no parent, and nothing it logs ever
# reaches the root logger. Counting on root silently reported "no windows
# evaluated" while the model was classifying a window every 350 ms.
_audio_logger.addHandler(windows)


def diagnose(counts):
    """Turn the window counts into a plain-language verdict."""
    if not counts:
        return ["No audio windows were evaluated - the microphone is not "
                "reaching the model."]
    if counts.get(WAKE_WORD, 0):
        return []
    if counts.get("other", 0):
        return ["Speech was heard, but none of it matched the wake word. The "
                "model shipped with the board was trained on one speaker: "
                "lower CONFIDENCE, or train your own model."]
    if counts.get("background", 0):
        return ["Only background noise, no speech - speak closer to the "
                "microphone, or check the capture gain."]
    return []

stt = None
tts = None
spotter = None
ready = False
busy = False
wake_count = 0
last_wake_at = time.time()
state_lock = threading.Lock()

# The light is state, not a flash: it keeps showing the last colour a command
# asked for, and goes back to it when a command is not understood.
current_color = (0, 0, 0)
current_name = "off"


def set_light(red, green, blue):
    """Send one RGB value to the Arduino sketch."""
    Bridge.call("set_rgb", int(red), int(green), int(blue))


def prepare_microphone():
    """Put the capture route and gain into a known-good state.

    The saved system state leaves the capture gain at its minimum, and a
    speech recognition brick from another app can leave the capture route
    switched off entirely. Either way the model would run happily and hear
    nothing - measured on this kit, normal speech registered RMS 67 with the
    saved gain and RMS 1200 with the values below.
    """
    settings = (
        ("MultiMedia3 Mixer TX_CODEC_DMA_TX_3", "1"),
        ("TX DEC0 MUX", "SWR_MIC"),
        ("TX SMIC MUX0", "SWR_MIC1"),
        ("TX_AIF1_CAP Mixer DEC0", "1"),
        ("ADC2 Switch", "1"),
        ("ADC2 MUX", "INP2"),
        ("ADC2_MIXER Switch", "1"),
        ("ADC2 Volume", "8"),
        ("TX_DEC0 Volume", "100"),
    )
    try:
        applied = 0
        missing = []
        for name, value in settings:
            # Each setting on its own: one name that this audio codec does not
            # expose must not stop the rest of the route from being applied.
            # Previously a single unknown name silently skipped the gain
            # settings that come after it, leaving the model listening to a
            # muted microphone.
            try:
                result = subprocess.run(
                    ["amixer", "-c0", "cset", f"iface=MIXER,name={name}", value],
                    capture_output=True, timeout=10,
                )
                if result.returncode == 0:
                    applied += 1
                else:
                    missing.append(name)
            except Exception:
                missing.append(name)

        print(f"[MIC] Capture route and gain applied "
              f"({applied}/{len(settings)} settings).", flush=True)
        if missing:
            print(f"[MIC] This audio codec does not expose: "
                  f"{', '.join(missing)}", flush=True)
            print("[MIC] If the model reports no audio windows, start here.",
                  flush=True)
    except Exception as error:
        print(f"[MIC] Could not configure the microphone: "
              f"{type(error).__name__}: {error}", flush=True)


def check_microphone():
    """Capture briefly with the same device the keyword spotting brick uses.

    The brick creates its microphone implicitly, as the first plugged device
    (USB first, then the built-in one). If that resolution picks the wrong
    device on this board, the model never receives a single sample and the app
    looks dead while every line of it reports success. Capturing here, before
    the brick starts, turns that into a concrete line in the console: the
    device name the platform resolved, the volume, and the peak level that
    actually arrived.
    """
    try:
        from arduino.app_peripherals.microphone import Microphone
    except Exception as error:
        print(f"[MIC] Platform microphone unavailable: "
              f"{type(error).__name__}: {error}", flush=True)
        return

    mic = None
    try:
        mic = Microphone(0, sample_rate=16000, channels=1)
        print(f"[MIC] Platform microphone 0 resolves to "
              f"{mic.device_stable_ref} ({mic.name}), volume {mic.volume}%.",
              flush=True)
        mic.start()
        peak = 0
        total = 0
        clipped = 0
        samples = 0
        started = time.time()
        for chunk in mic.stream():
            if chunk is not None and len(chunk):
                try:
                    level = abs(chunk.astype("int32"))
                    peak = max(peak, int(level.max()))
                    total += int(level.sum())
                    clipped += int((level >= 32000).sum())
                except Exception:
                    pass
                samples += len(chunk)
            if time.time() - started >= MIC_CHECK_SECONDS:
                break
        mic.stop()
        average = total / samples if samples else 0.0
        print(f"[MIC] Captured {samples} samples in "
              f"{MIC_CHECK_SECONDS:.1f}s: peak {peak} of 32767, "
              f"average {average:.0f}, pinned at full scale "
              f"{100.0 * clipped / samples if samples else 0:.1f}%.", flush=True)
        if samples == 0:
            print("[MIC] No samples arrived, so the model cannot hear "
                  "anything. Point the brick at a working device with "
                  "Microphone(JACK_MIC_1) or use a USB microphone.", flush=True)
        elif samples and clipped * 100.0 / samples > 1.0:
            print("[MIC] A slice of every chunk is pinned at full scale: the "
                  "capture is clipping, so words arrive distorted. Lower "
                  "TX_DEC0 Volume in prepare_microphone() first.", flush=True)
        elif average < 50:
            print("[MIC] The samples are almost silent: raise the capture "
                  "gain before blaming the model.", flush=True)
    except Exception as error:
        print(f"[MIC] Platform microphone failed: "
              f"{type(error).__name__}: {error}", flush=True)
    finally:
        if mic is not None:
            try:
                mic.stop()
            except Exception:
                pass


def on_wake():
    """The model is sure enough: wake the assistant."""
    global wake_count, last_wake_at
    with state_lock:
        if busy or not ready:
            return
        wake_count += 1
        last_wake_at = time.time()
    threading.Thread(target=handle_command, daemon=True).start()


def listen_for_command():
    """Wake, record one command, print it, act on it."""
    print("", flush=True)
    print(f'[WAKE] "{WAKE_LABEL}" recognised - waking up.', flush=True)
    if tts is None:
        print("[TTS] No speech brick - skipping the spoken cue.", flush=True)
    else:
        try:
            tts.say("I'm here.")
            print("[TTS] I'm here.", flush=True)
        except Exception as error:
            print(f"[TTS] failed: {type(error).__name__}: {error}", flush=True)

    set_light(0, 60, 0)          # visible sign that it is awake
    time.sleep(0.3)

    if stt is None:
        print("[STT] Speech recognition is not available, so no command can "
              "be recorded. The wake word and the light still work.",
              flush=True)
        set_light(*current_color)
        return

    print("[LISTENING] Speak your command now...", flush=True)
    try:
        stt.reset()
        stt.start_listening()
        time.sleep(COMMAND_SECONDS)
        stt.stop_listening()
        result = stt.get_result(timeout=60)
    except Exception as error:
        print(f"[STT] failed: {type(error).__name__}: {error}", flush=True)
        set_light(*current_color)
        return

    if isinstance(result, dict):
        result = result.get("text", "")
    heard = str(result).strip() if result else ""

    print(f'[HEARD] {heard if heard else "(nothing recognised)"}', flush=True)
    if not run_command(heard):
        set_light(*current_color)
        print(f"[ACTION] Light stays {current_name}.", flush=True)


def apply_light(name, color):
    """Show a colour and remember it as the light's current state."""
    global current_color, current_name
    set_light(*color)
    current_color = color
    current_name = name


def run_command(text):
    """Act on a spoken command. Returns True if the light changed."""
    command = " ".join(str(text).lower().split())
    words = command.split()

    for name, color in COLOR_PRESETS.items():
        if name in command:
            apply_light(name, color)
            print(f"[ACTION] Light is now {name}.", flush=True)
            return True

    if "off" in command:
        apply_light("off", (0, 0, 0))
        print("[ACTION] Light off.", flush=True)
        return True

    if "on" in words:
        if current_color == (0, 0, 0):
            apply_light("white", COLOR_PRESETS["white"])
            print("[ACTION] Light on (white).", flush=True)
        else:
            set_light(*current_color)
            print(f"[ACTION] Light on ({current_name}).", flush=True)
        return True

    if text:
        print("[ACTION] No supported light command in that sentence.",
              flush=True)
    return False


def handle_command():
    """Run one wake interaction without blocking the detector callback."""
    global busy
    with state_lock:
        if busy:
            return
        busy = True
    try:
        listen_for_command()
    except Exception as error:
        print(f"[ERROR] {type(error).__name__}: {error}", flush=True)
    finally:
        # The light is deliberately left alone here: the colour the command
        # asked for is the result of the interaction. Clearing it in this
        # block made every command flash for a moment and then go dark.
        busy = False
        print('[READY] Waiting for "Hey Arduino"...', flush=True)


def heartbeat():
    """Prove the microphone and the model are alive.

    Without this the console goes quiet whenever the wake word is not
    recognised, and a working app is indistinguishable from a dead one.
    """
    while True:
        time.sleep(HEARTBEAT_SECONDS)
        with state_lock:
            wakes = wake_count
            since = time.time() - last_wake_at

        if not ready:
            print("[WAIT] Still starting up...", flush=True)
            continue
        if busy:
            print(f"[BUSY] Handling a command. (wakes={wakes})", flush=True)
        else:
            print(f"[LISTENING] Microphone active. wakes={wakes}, "
                  f"last wake {since:.0f}s ago.", flush=True)

        counts, best = windows.take()
        summary = ", ".join(
            f"{label} {count}x (best {best.get(label, 0.0):.0f}%)"
            for label, count in sorted(counts.items(),
                                       key=lambda item: -item[1])
        ) or "no windows evaluated"
        print(f"[HEARD] {summary}", flush=True)
        for line in diagnose(counts):
            print(f"        {line}", flush=True)


def bench_run():
    """Bench aid: run one cycle without saying the wake word."""
    time.sleep(BENCH_WAKE_AFTER_SECONDS)
    try:
        if BENCH_COMMAND:
            print(f'[BENCH] Applying "{BENCH_COMMAND}" as if it had been '
                  f"heard.", flush=True)
            if not run_command(BENCH_COMMAND):
                print("[BENCH] That sentence is not a light command.",
                      flush=True)
        else:
            print("[BENCH] Waking without the wake word.", flush=True)
            on_wake()
    except Exception as error:
        print(f"[BENCH] failed: {type(error).__name__}: {error}", flush=True)


def initialize():
    """Bring up speech recognition, speech and the console banner."""
    global stt, tts, spotter, ready

    if STT is None:
        print("[WARN] Speech recognition brick is not part of this build.",
              flush=True)
    else:
        try:
            print("[STARTING] Loading speech recognition for commands...",
                  flush=True)
            stt = STT(type="local_fast", language="en")
            stt.reset()
            print("[OK] Speech recognition loaded.", flush=True)
        except Exception as error:
            stt = None
            print(f"[WARN] Speech recognition failed, spoken commands will be "
                  f"skipped: {type(error).__name__}: {error}", flush=True)

    if EdgeTTS is None:
        print("[WARN] Text to speech brick is not part of this build.",
              flush=True)
    else:
        try:
            print("[STARTING] Initializing text to speech...", flush=True)
            tts = EdgeTTS()
            tts.set_voice("en-US-JennyNeural")
            tts.set_volume(50)
            print("[OK] Text to speech ready.", flush=True)
        except Exception as error:
            tts = None
            print(f"[WARN] Text to speech failed, commands still work: "
                  f"{type(error).__name__}: {error}", flush=True)

    if spotter is None:
        print("[STARTUP ERROR] No keyword spotting model was opened, so the "
              "wake word cannot work in this run.", flush=True)
        return

    set_light(0, 0, 0)
    ready = True
    print("", flush=True)
    print(f'Say "{WAKE_LABEL}". The model prints its opinion for every window',
          flush=True)
    print("it evaluates, so you can see what it made of your pronunciation:",
          flush=True)
    print("  Keyword 'hey_arduino' detected with confidence N%   <- woke up",
          flush=True)
    print("  Keyword 'background' detected ...                    <- it heard",
          flush=True)
    print("                                                         nothing",
          flush=True)
    print("  Keyword 'other' detected ...                         <- speech, ",
          flush=True)
    print("                                                         not the",
          flush=True)
    print("                                                         wake word",
          flush=True)
    print("", flush=True)
    print('[READY] Waiting for "Hey Arduino"...', flush=True)


def open_spotter():
    """Create the keyword spotting brick before App.run() starts the loops.

    The brick's microphone reader and its inference loop are registered as app
    loops, and App.run() collects those when it starts. Creating the brick
    afterwards, from the initialize thread, left both loops unregistered: the
    console said keyword spotting was running while the model never received a
    single sample and never printed a single line about it. The brick has to
    exist before App.run(), exactly as in Arduino's own examples.
    """
    global spotter
    try:
        print("[STARTING] Opening the keyword spotting model...", flush=True)
        spotter = KeywordSpotting(confidence=CONFIDENCE)
        spotter.on_detect(WAKE_WORD, on_wake)
        print(f"[OK] Keyword spotting running for \"{WAKE_LABEL}\" "
              f"(wake threshold {CONFIDENCE:.2f}).", flush=True)
    except Exception as error:
        spotter = None
        print(f"[STARTUP ERROR] Keyword spotting failed: "
              f"{type(error).__name__}: {error}", flush=True)


prepare_microphone()
check_microphone()
open_spotter()

threading.Thread(target=heartbeat, daemon=True).start()
threading.Thread(target=initialize, daemon=True).start()
if BENCH_WAKE_AFTER_SECONDS > 0:
    threading.Thread(target=bench_run, daemon=True).start()

App.run()
