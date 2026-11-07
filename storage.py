"""JSON persistence helpers for quiz state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

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


def load_state(path: Path, output_fn: Callable[[str], None] | None = None) -> dict:
    def recover() -> dict:
        if output_fn:
            output_fn("저장 데이터가 없거나 손상되어 기본 퀴즈로 시작합니다.")
        return default_state()

    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError, UnicodeDecodeError):
        return recover()
    return state if _is_valid_state(state) else recover()


def save_state(path: Path, state: dict) -> None:
    path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
