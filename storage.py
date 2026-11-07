"""JSON persistence helpers for quiz state."""

from __future__ import annotations

import json
from pathlib import Path

from quiz import Quiz, default_quizzes


def default_state() -> dict:
    return {
        "quizzes": [quiz.to_dict() for quiz in default_quizzes()],
        "best_score": 0,
        "history": [],
    }


def _is_valid_state(state: object) -> bool:
    if not isinstance(state, dict):
        return False
    if not {"quizzes", "best_score", "history"}.issubset(state):
        return False
    if not isinstance(state["quizzes"], list) or not isinstance(state["history"], list):
        return False
    if not isinstance(state["best_score"], int) or state["best_score"] < 0:
        return False
    try:
        [Quiz.from_dict(item) for item in state["quizzes"]]
    except (KeyError, TypeError, ValueError):
        return False
    return all(isinstance(item, dict) for item in state["history"])


def load_state(path: Path) -> dict:
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError, UnicodeDecodeError):
        return default_state()
    return state if _is_valid_state(state) else default_state()


def save_state(path: Path, state: dict) -> None:
    path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
