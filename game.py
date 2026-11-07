"""Game orchestration for the Korean movie quiz."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from quiz import Quiz
from storage import load_state, save_state


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

    def play_quiz(self, quizzes: list[Quiz], count: int) -> dict:
        selected = quizzes[:count]
        correct = 0
        for number, quiz in enumerate(selected, 1):
            self.output_fn(f"\n[문제 {number}/{len(selected)}]\n{quiz.display()}")
            choice = int(self.input_fn("정답 번호: ").strip())
            if quiz.is_correct(choice):
                correct += 1
                self.output_fn("정답입니다!")
            else:
                self.output_fn(f"오답입니다. 정답은 {quiz.answer}번입니다.")
        result = {
            "question_count": len(selected),
            "correct": correct,
            "score": correct,
        }
        self.best_score = max(self.best_score, correct)
        return result

    def run(self) -> None:
        self.output_fn("🎬 한국 영화 퀴즈 게임")
        while True:
            self.output_fn("\n1. 퀴즈 풀기\n2. 퀴즈 추가\n3. 퀴즈 목록\n4. 점수 확인\n5. 종료")
            choice = int(self.input_fn("선택: ").strip())
            if choice == 1:
                self.play_quiz(self.quizzes, len(self.quizzes))
            elif choice == 5:
                self.save()
                self.output_fn("게임을 종료합니다.")
                return
            else:
                self.output_fn("이 기능은 다음 단계에서 구현합니다.")
