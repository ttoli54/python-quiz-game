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


def default_quizzes() -> list[Quiz]:
    return [
        Quiz(
            "영화 '기생충'의 감독은 누구인가요?",
            ["박찬욱", "봉준호", "최동훈", "윤제균"],
            2,
            "아카데미 감독상을 받은 감독입니다.",
        ),
        Quiz(
            "영화 '올드보이'의 감독은 누구인가요?",
            ["박찬욱", "김지운", "홍상수", "장준환"],
            1,
            "복수 3부작으로 유명한 감독입니다.",
        ),
        Quiz(
            "영화 '부산행'에서 주인공 일행이 향하는 도시는 어디인가요?",
            ["대전", "대구", "부산", "광주"],
            3,
            "영화 제목에 들어 있는 도시입니다.",
        ),
        Quiz(
            "영화 '국제시장'의 주인공 이름은 무엇인가요?",
            ["덕수", "만식", "동수", "영호"],
            1,
            "주인공의 이름은 두 글자입니다.",
        ),
        Quiz(
            "영화 '택시운전사'의 시대적 배경이 된 사건은 무엇인가요?",
            ["4·19 혁명", "5·18 민주화운동", "6월 민주항쟁", "IMF 외환위기"],
            2,
            "1980년 광주에서 일어난 민주화운동입니다.",
        ),
        Quiz(
            "영화 '7번방의 선물'에서 주인공의 이름은 무엇인가요?",
            ["용구", "민재", "상현", "철수"],
            1,
            "딸 예승의 아버지입니다.",
        ),
    ]
