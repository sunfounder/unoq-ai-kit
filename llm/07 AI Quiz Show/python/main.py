# SPDX-FileCopyrightText: Copyright (C) SunFounder
#
# SPDX-License-Identifier: MPL-2.0

"""AI Quiz Show

The LLM creates an age-friendly three-choice question. Players answer with
the A/B/C buttons in the Web UI. RGB, buzzer, TTS, and the scoreboard provide
immediate feedback.
"""

import json
import re
import threading

from arduino.app_bricks.cloud_llm import CloudLLM
from arduino.app_bricks.web_ui import WebUI
from arduino.app_utils import App, Bridge, Logger

from sunfounder_tts import EdgeTTS


TTS_VOICE = "en-US-JennyNeural"

QUIZ_SYSTEM_PROMPT = (
    "You create clear, age-friendly general-knowledge multiple-choice "
    "questions for students. Use varied topics such as science, nature, "
    "technology, geography, language, and everyday life. Each question must "
    "have exactly three choices and exactly one correct answer. Avoid trick "
    "questions, politics, violence, adult topics, and time-sensitive facts. "
    "Return only valid JSON with this exact structure: "
    "{\"question\":\"...\",\"choices\":{\"A\":\"...\","
    "\"B\":\"...\",\"C\":\"...\"},\"answer\":\"A\","
    "\"explanation\":\"One short sentence\"}. "
    "Keep the question, choices, and explanation concise."
)


logger = Logger("AIQuizShow")
ui = WebUI()

llm = CloudLLM(
    model="openai:gpt-4o-mini",
    system_prompt=QUIZ_SYSTEM_PROMPT,
    temperature=0.8,
    max_tokens=180,
)
llm.with_memory(max_messages=0)

tts = EdgeTTS()
tts.set_voice(TTS_VOICE)
tts.set_volume(50)

state_lock = threading.Lock()
current_quiz = None
score = 0
questions_answered = 0
busy = False
answered = False
recent_questions = []


def send_state(state, message, selected="", result="", room=None):
    """Send the complete quiz state to one browser or all browsers."""
    with state_lock:
        quiz = (
            {
                "question": current_quiz["question"],
                "choices": dict(current_quiz["choices"]),
            }
            if current_quiz
            else None
        )
        payload = {
            "state": state,
            "message": message,
            "quiz": quiz,
            "score": score,
            "questions_answered": questions_answered,
            "answered": answered,
            "selected": selected,
            "result": result,
        }
    ui.send_message("quiz_state", payload, room=room)


def hardware_feedback(code):
    try:
        Bridge.call("quiz_feedback", code)
    except Exception as error:
        logger.warning(f"Hardware feedback unavailable: {error}")


def speak(text):
    try:
        tts.say(text)
    except Exception as error:
        logger.warning(f"TTS unavailable: {error}")


def parse_quiz(text):
    """Parse and validate one multiple-choice question."""
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("The AI did not return quiz JSON.")

    data = json.loads(match.group(0))
    question = " ".join(str(data.get("question", "")).split())
    choices = data.get("choices", {})
    choices = {
        letter: " ".join(str(choices.get(letter, "")).split())
        for letter in ("A", "B", "C")
    }
    answer = str(data.get("answer", "")).strip().upper()
    explanation = " ".join(str(data.get("explanation", "")).split())

    if not question or any(not choices[letter] for letter in choices):
        raise ValueError("The AI returned an incomplete question.")
    if answer not in choices:
        raise ValueError("The AI returned an invalid correct answer.")
    if not explanation:
        explanation = f"The correct answer is {answer}: {choices[answer]}."

    return {
        "question": question[:180],
        "choices": {key: value[:100] for key, value in choices.items()},
        "answer": answer,
        "explanation": explanation[:180],
    }


def create_question(sid):
    global busy, answered, current_quiz
    try:
        send_state("generating", "AI is creating a new question...", room=sid)

        with state_lock:
            avoid = list(recent_questions[-5:])

        prompt = "Create one new three-choice quiz question."
        if avoid:
            prompt += " Do not repeat these questions: " + " | ".join(avoid)

        quiz = parse_quiz(llm.chat(message=prompt))

        with state_lock:
            current_quiz = quiz
            answered = False
            recent_questions.append(quiz["question"])

        hardware_feedback(1)
        send_state("speaking", "Listen to the question...", room=sid)

        choices = quiz["choices"]
        spoken_question = (
            f"{quiz['question']} "
            f"A: {choices['A']}. "
            f"B: {choices['B']}. "
            f"C: {choices['C']}."
        )
        speak(spoken_question)

        send_state(
            "ready",
            "Choose A, B, or C on the page.",
            room=sid,
        )

    except Exception as error:
        logger.exception(f"Question generation failed: {error}")
        hardware_feedback(3)
        send_state(
            "error",
            f"Unable to create a question: {type(error).__name__}: {error}",
            room=sid,
        )

    finally:
        with state_lock:
            busy = False


def request_question(sid, _data):
    global busy
    with state_lock:
        if busy:
            return
        busy = True

    threading.Thread(target=create_question, args=(sid,), daemon=True).start()


def process_answer(sid, selected):
    global busy, answered, score, questions_answered

    with state_lock:
        if busy or answered or not current_quiz:
            return
        busy = True
        answered = True
        quiz = dict(current_quiz)

    correct = selected == quiz["answer"]

    with state_lock:
        questions_answered += 1
        if correct:
            score += 1

    hardware_feedback(2 if correct else 3)

    if correct:
        status = "Correct!"
        speech = f"Correct! {quiz['explanation']}"
    else:
        correct_answer = quiz["answer"]
        status = f"The correct answer is {correct_answer}."
        speech = f"Not quite. The correct answer is {correct_answer}. {quiz['explanation']}"

    send_state(
        "correct" if correct else "wrong",
        status,
        selected=selected,
        result=quiz["explanation"],
        room=sid,
    )

    speak(speech)

    with state_lock:
        busy = False

    send_state(
        "complete",
        "Choose NEW QUESTION to continue.",
        selected=selected,
        result=quiz["explanation"],
        room=sid,
    )


def submit_answer(sid, data):
    selected = str((data or {}).get("answer", "")).strip().upper()
    if selected not in ("A", "B", "C"):
        return
    threading.Thread(
        target=process_answer,
        args=(sid, selected),
        daemon=True,
    ).start()


def send_current_state(sid, _data):
    send_state(
        "ready",
        (
            "Choose A, B, or C."
            if current_quiz and not answered
            else "Choose NEW QUESTION to begin."
        ),
        room=sid,
    )


def reset_quiz(sid, _data):
    global score, questions_answered, current_quiz, answered
    with state_lock:
        if busy:
            return
        score = 0
        questions_answered = 0
        current_quiz = None
        answered = False
    hardware_feedback(0)
    send_state("ready", "Score reset. Choose NEW QUESTION to begin.", room=sid)


ui.on_message("get_state", send_current_state)
ui.on_message("new_question", request_question)
ui.on_message("submit_answer", submit_answer)
ui.on_message("reset_quiz", reset_quiz)

print("AI Quiz Show ready.")
print("Open App Launch and choose NEW QUESTION to begin.")

App.run()
