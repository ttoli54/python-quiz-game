"""Game orchestration for the Korean movie quiz."""

from __future__ import annotations

import random
from datetime import datetime
from pathlib import Path
from typing import Callable

from quiz import Quiz
from storage import load_state, save_state


class InputClosed(Exception):
    """Raised when the console input stream is interrupted or closed."""


def read_int(
    prompt: str,
    minimum: int,
    maximum: int,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> int:
    while True:
        try:
            raw = input_fn(prompt).strip()
        except (KeyboardInterrupt, EOFError) as error:
            raise InputClosed from error
        if not raw:
            output_fn("입력값을 입력해주세요.")
            continue
        try:
            value = int(raw)
        except ValueError:
            output_fn("숫자를 입력해주세요.")
            continue
        if not minimum <= value <= maximum:
            output_fn(f"{minimum}-{maximum} 사이의 숫자를 입력해주세요.")
            continue
        return value


class QuizGame:
    def __init__(
        self,
        state_path: Path,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
    ) -> None:
        self.state_path = Path(state_path)
        self.input_fn = input_fn
        self.output_fn = output_fn
        state = load_state(self.state_path)
        self.quizzes = [Quiz.from_dict(item) for item in state["quizzes"]]
        self.best_score = state["best_score"]
        self.history = state["history"]

    def _state(self) -> dict:
        return {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
            "history": self.history,
        }

    def save(self) -> None:
        try:
            save_state(self.state_path, self._state())
        except OSError as error:
            self.output_fn(f"저장에 실패했습니다: {error}")

    def _read_text(self, prompt: str) -> str:
        while True:
            try:
                value = self.input_fn(prompt).strip()
            except (KeyboardInterrupt, EOFError) as error:
                raise InputClosed from error
            if value:
                return value
            self.output_fn("입력값은 비어 있을 수 없습니다.")

    def add_quiz(self) -> None:
        self.output_fn("새로운 퀴즈를 추가합니다.")
        question = self._read_text("문제: ")
        choices = [self._read_text(f"선택지 {index}: ") for index in range(1, 5)]
        answer = read_int("정답 번호(1-4): ", 1, 4, self.input_fn, self.output_fn)
        hint = self._read_text("힌트: ")
        self.quizzes.append(Quiz(question, choices, answer, hint))
        self.save()
        self.output_fn("퀴즈가 추가되었습니다.")

    def list_quizzes(self) -> None:
        if not self.quizzes:
            self.output_fn("등록된 퀴즈가 없습니다.")
            return
        self.output_fn(f"등록된 퀴즈 ({len(self.quizzes)}개)")
        for index, quiz in enumerate(self.quizzes, 1):
            self.output_fn(f"{index}. {quiz.question}")

    def ask_question_count(self) -> int:
        if not self.quizzes:
            self.output_fn("등록된 퀴즈가 없어 문제 수를 선택할 수 없습니다.")
            return 0
        return read_int("몇 문제를 풀까요? ", 1, len(self.quizzes), self.input_fn, self.output_fn)

    def delete_quiz(self) -> None:
        if not self.quizzes:
            self.output_fn("삭제할 퀴즈가 없습니다.")
            return
        self.list_quizzes()
        index = read_int("삭제할 퀴즈 번호: ", 1, len(self.quizzes), self.input_fn, self.output_fn)
        deleted = self.quizzes.pop(index - 1)
        self.save()
        self.output_fn(f"퀴즈를 삭제했습니다: {deleted.question}")

    def show_scores(self) -> None:
        self.output_fn(f"최고 점수: {self.best_score}점")
        if not self.history:
            self.output_fn("아직 게임 기록이 없습니다.")
            return
        self.output_fn(f"게임 기록: {len(self.history)}회")
        for record in self.history[-5:]:
            self.output_fn(
                f"{record.get('timestamp', '-')}: "
                f"{record.get('correct', 0)}/{record.get('question_count', 0)}점"
            )

    def play_quiz(self, quizzes: list[Quiz], count: int) -> dict:
        selected = random.sample(quizzes, min(count, len(quizzes)))
        correct = 0
        hints = 0
        for number, quiz in enumerate(selected, 1):
            self.output_fn(f"\n[문제 {number}/{len(selected)}]\n{quiz.display()}")
            try:
                wants_hint = self.input_fn("힌트를 보시겠습니까? (y/n): ").strip().lower() == "y"
            except (KeyboardInterrupt, EOFError) as error:
                raise InputClosed from error
            if wants_hint:
                hints += 1
                self.output_fn(f"힌트: {quiz.hint}")
            choice = read_int("정답 번호: ", 1, 4, self.input_fn, self.output_fn)
            if quiz.is_correct(choice):
                correct += 1
                self.output_fn("정답입니다!")
            else:
                self.output_fn(f"오답입니다. 정답은 {quiz.answer}번입니다.")
        result = {
            "question_count": len(selected),
            "correct": correct,
            "hints": hints,
            "score": max(0, correct - hints),
        }
        result["timestamp"] = datetime.now().isoformat(timespec="seconds")
        self.best_score = max(self.best_score, result["score"])
        self.history.append(result.copy())
        self.save()
        return result

    def run(self) -> None:
        self.output_fn("🎬 한국 영화 퀴즈 게임")
        try:
            while True:
                self.output_fn(
                    "\n1. 퀴즈 풀기\n2. 퀴즈 추가\n3. 퀴즈 목록\n"
                    "4. 점수 확인\n5. 퀴즈 삭제\n6. 종료"
                )
                choice = read_int("선택: ", 1, 6, self.input_fn, self.output_fn)
                if choice == 1:
                    count = self.ask_question_count()
                    if count:
                        self.play_quiz(self.quizzes, count)
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.list_quizzes()
                elif choice == 4:
                    self.show_scores()
                elif choice == 5:
                    self.delete_quiz()
                elif choice == 6:
                    self.save()
                    self.output_fn("게임을 종료합니다.")
                    return
        except InputClosed:
            self.save()
            self.output_fn("입력이 종료되어 현재 상태를 저장하고 안전하게 종료합니다.")
