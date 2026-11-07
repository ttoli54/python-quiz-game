"""Quiz question model and default data."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Quiz:
    question: str
    choices: list[str]
    answer: int
    hint: str = ""

    def __post_init__(self) -> None:
        if not self.question.strip():
            raise ValueError("질문은 비어 있을 수 없습니다.")
        if len(self.choices) != 4:
            raise ValueError("선택지는 정확히 4개여야 합니다.")
        if any(not choice.strip() for choice in self.choices):
            raise ValueError("선택지는 비어 있을 수 없습니다.")
        if self.answer not in range(1, 5):
            raise ValueError("정답 번호는 1부터 4까지여야 합니다.")

    def display(self) -> str:
        lines = [self.question]
        lines.extend(f"{index}. {choice}" for index, choice in enumerate(self.choices, 1))
        return "\n".join(lines)

    def is_correct(self, choice: int) -> bool:
        return choice == self.answer

    def to_dict(self) -> dict:
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Quiz":
        return cls(
            question=str(data["question"]),
            choices=list(data["choices"]),
            answer=int(data["answer"]),
            hint=str(data.get("hint", "")),
        )
