"""JSON persistence helpers for quiz state."""

from __future__ import annotations

import json
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Callable

from quiz import Quiz, default_quizzes

RECOVERY_MESSAGE = "저장 데이터가 없거나 손상되어 기본 퀴즈로 시작합니다."
BACKUP_FAILURE_MESSAGE = " 손상된 원본 백업에는 실패했습니다."


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
    def recover(with_backup: bool) -> dict:
        backup_path = None
        if with_backup and path.exists():
            backup_path = path.with_name(
                f"{path.stem}.corrupt-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}{path.suffix}"
            )
            try:
                shutil.copy2(path, backup_path)
            except OSError:
                backup_path = None
        if output_fn:
            message = RECOVERY_MESSAGE
            if backup_path:
                message += f" 손상된 원본은 {backup_path.name}으로 백업했습니다."
            elif with_backup:
                message += BACKUP_FAILURE_MESSAGE
            output_fn(message)
        return default_state()

    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return recover(False)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return recover(True)
    return state if _is_valid_state(state) else recover(True)


def save_state(path: Path, state: dict) -> None:
    temporary_path = path.with_name(f"{path.stem}.tmp-{uuid.uuid4().hex}{path.suffix}")
    try:
        temporary_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()
