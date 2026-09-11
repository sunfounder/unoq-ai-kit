# SPDX-FileCopyrightText: Copyright (C) Arduino s.r.l. and/or its affiliated companies
#
# SPDX-License-Identifier: MPL-2.0

"""AI Rock Paper Scissors using the Hand Gestures detection model."""

import random
import threading
import time
from datetime import UTC, datetime

from arduino.app_utils import App, Bridge
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from arduino.app_bricks.web_ui import WebUI
from arduino.app_peripherals.camera import Camera


CONFIDENCE_THRESHOLD = 0.45
STABLE_SECONDS = 0.25
RESULT_SECONDS = 3.0

MOVES = ("rock", "paper", "scissors")
WINNING_MOVE = {
    "rock": "scissors",
    "paper": "rock",
    "scissors": "paper",
}

ui = WebUI()
state_lock = threading.RLock()

phase = "waiting_start"
message = "Press START GAME to begin"
countdown = 0
live_gesture = "none"
live_confidence = 0
player_move = ""
computer_move = ""
round_result = ""
scores = {"player": 0, "ties": 0, "computer": 0}

candidate_gesture = None
candidate_since = 0.0
last_live_update = 0.0
last_debug_update = 0.0


def normalize_gesture(label):
    """Map the model labels to the three moves used by the game."""
    normalized = str(label).lower().replace("_", " ").replace("-", " ").strip()

    if "peace" in normalized or "v sign" in normalized:
        return "scissors"
    if "five" in normalized or "open hand" in normalized:
        return "paper"
    if "fist" in normalized or normalized == "neutral":
        return "rock"
    return None


def best_raw_detection(detections):
    """Return the model's strongest raw label for console diagnostics."""
    best_label = "none"
    best_confidence = 0.0

    for label, instances in detections.items():
        for instance in instances:
            confidence = float(instance.get("confidence", 0))
            if confidence > 1:
                confidence /= 100
            if confidence > best_confidence:
                best_label = str(label)
                best_confidence = confidence

    return best_label, best_confidence


def best_gesture(detections):
    """Return (game gesture, confidence) for the best supported detection."""
    best_name = None
    best_confidence = 0.0

    for label, instances in detections.items():
        gesture = normalize_gesture(label)
        if gesture is None:
            continue

        for instance in instances:
            confidence = float(instance.get("confidence", 0))
            if confidence > 1:
                confidence /= 100
            if confidence > best_confidence:
                best_name = gesture
                best_confidence = confidence

    if best_confidence < CONFIDENCE_THRESHOLD:
        return None, 0.0
    return best_name, best_confidence


def game_data():
    with state_lock:
        return {
            "phase": phase,
            "message": message,
            "countdown": countdown,
            "gesture": live_gesture,
            "confidence": live_confidence,
            "player_move": player_move,
            "computer_move": computer_move,
            "result": round_result,
            "scores": dict(scores),
            "timestamp": datetime.now(UTC).isoformat(),
        }


def send_game_state(client=None):
    data = game_data()
    if client is None:
        ui.send_message("game_state", data)
    else:
        ui.send_message("game_state", data, client)


def clear_candidate():
    global candidate_gesture, candidate_since
    candidate_gesture = None
    candidate_since = 0.0


def countdown_worker():
    """Show a short countdown, then accept one game move."""
    global phase, message, countdown

    for number in (3, 2, 1):
        with state_lock:
            if phase != "countdown":
                return
            countdown = number
            message = f"Get ready — {number}"
        send_game_state()
        time.sleep(0.7)

    with state_lock:
        if phase != "countdown":
            return
        phase = "waiting_move"
        countdown = 0
        message = "Show rock, paper, or scissors"
        clear_candidate()

    Bridge.call("round_start")
    send_game_state()


def begin_round():
    global phase, message, countdown, player_move, computer_move, round_result

    with state_lock:
        if phase != "waiting_start":
            return
        phase = "countdown"
        message = "Get ready"
        countdown = 3
        player_move = ""
        computer_move = ""
        round_result = ""
        clear_candidate()

    print("[GAME] New round started from the Web UI.", flush=True)
    Bridge.call("ready")
    threading.Thread(target=countdown_worker, daemon=True).start()


def compare_moves(player, computer):
    if player == computer:
        return "tie"
    if WINNING_MOVE[player] == computer:
        return "win"
    return "lose"


def return_to_start_worker():
    global phase, message, countdown, player_move, computer_move, round_result

    time.sleep(RESULT_SECONDS)
    with state_lock:
        if phase != "result":
            return
        phase = "waiting_start"
        message = "Press START GAME to play again"
        countdown = 0
        player_move = ""
        computer_move = ""
        round_result = ""
        clear_candidate()

    Bridge.call("ready")
    send_game_state()


def finish_round(move):
    global phase, message, player_move, computer_move, round_result

    computer = random.choice(MOVES)
    result = compare_moves(move, computer)

    with state_lock:
        if phase != "waiting_move":
            return
        phase = "result"
        player_move = move
        computer_move = computer
        round_result = result

        if result == "win":
            scores["player"] += 1
            message = "You win!"
            result_code = 1
        elif result == "lose":
            scores["computer"] += 1
            message = "Computer wins!"
            result_code = 2
        else:
            scores["ties"] += 1
            message = "It is a tie!"
            result_code = 3

        clear_candidate()

    print(
        f"Round: player={move}, computer={computer}, result={result}",
        flush=True,
    )
    Bridge.call("show_result", result_code)
    send_game_state()
    threading.Thread(target=return_to_start_worker, daemon=True).start()


def on_detections(detections):
    """Track a stable gesture and advance the game state once."""
    global live_gesture, live_confidence, last_live_update
    global candidate_gesture, candidate_since, phase, last_debug_update

    gesture, confidence = best_gesture(detections)
    raw_label, raw_confidence = best_raw_detection(detections)
    now = time.monotonic()

    if now - last_debug_update >= 0.5:
        print(
            f"[AI] label={raw_label}, confidence={raw_confidence * 100:.0f}%",
            flush=True,
        )
        last_debug_update = now

    with state_lock:
        display_gesture = gesture or "none"
        display_confidence = round(confidence * 100)
        changed = (
            display_gesture != live_gesture
            or display_confidence != live_confidence
        )
        live_gesture = display_gesture
        live_confidence = display_confidence

        should_publish = changed or now - last_live_update >= 0.25
        if should_publish:
            last_live_update = now

        valid_for_phase = phase == "waiting_move" and gesture in MOVES

        if not valid_for_phase:
            clear_candidate()
            trigger = None
        elif candidate_gesture != gesture:
            candidate_gesture = gesture
            candidate_since = now
            trigger = None
        elif now - candidate_since >= STABLE_SECONDS:
            trigger = gesture
            # Change phase immediately so this held gesture cannot retrigger.
            phase = "resolving"
            clear_candidate()
        else:
            trigger = None

    if should_publish:
        send_game_state()

    if trigger in MOVES:
        with state_lock:
            phase = "waiting_move"
        finish_round(trigger)


def on_get_state(client, data):
    send_game_state(client)


def on_start_round(client, data):
    begin_round()


def on_reset_score(client, data):
    global phase, message, countdown, player_move, computer_move, round_result

    with state_lock:
        scores.update(player=0, ties=0, computer=0)
        phase = "waiting_start"
        message = "Score reset — press START GAME"
        countdown = 0
        player_move = ""
        computer_move = ""
        round_result = ""
        clear_candidate()

    Bridge.call("ready")
    send_game_state()


ui.on_message("get_state", on_get_state)
ui.on_message("start_round", on_start_round)
ui.on_message("reset_score", on_reset_score)

camera = Camera(adjustments=lambda frame: frame[::-1, :])
camera.start()

detection = VideoObjectDetection(
    camera,
    confidence=CONFIDENCE_THRESHOLD,
    debounce_sec=0.1,
)
detection.on_detect_all(on_detections)

print("✊ AI Rock Paper Scissors is running — open the Web UI.", flush=True)
App.run()
