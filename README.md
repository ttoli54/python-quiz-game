# 한국 영화 퀴즈 게임

Python 표준 라이브러리로 만든 4지선다 콘솔 퀴즈 게임입니다. 한국 영화를 주제로 골라 영화와 감독, 작품 속 배경을 문제로 구성했습니다.

## 주제를 고른 이유

한국 영화는 작품마다 감독·등장인물·시대적 배경이 달라서, 단순한 암기 문제와 배경을 생각하는 문제를 함께 만들기 좋았습니다. 문제를 직접 추가하면서 영화 정보를 다시 확인할 수 있다는 점도 이 과제의 학습 목적과 잘 맞았습니다.

## 실행 환경

- Python 3.10 이상
- 외부 패키지 없음
- Windows PowerShell에서 실행 가능

## 실행 방법

프로젝트 폴더에서 다음 명령을 실행합니다.

```powershell
python main.py
```

테스트는 다음 명령으로 실행합니다.

```powershell
python -m unittest -v
```

실행하면 메뉴에서 다음 기능을 선택할 수 있습니다.

1. 퀴즈 풀기
2. 퀴즈 추가
3. 퀴즈 목록
4. 점수 확인
5. 퀴즈 삭제
6. 종료

## 기능 목록

- 기본 한국 영화 퀴즈 6문제 제공
- 문제 순서를 `random.sample()`로 섞어 출제
- 풀 문제 수 선택
- 힌트 보기와 힌트 사용 시 1점 감점
- 새 퀴즈 추가 및 4개 선택지·정답·힌트 저장
- 등록된 퀴즈 삭제
- 최고 점수와 모든 게임 기록 저장
- 빈 입력, 문자 입력, 범위를 벗어난 숫자 재입력
- `Ctrl+C`와 `EOFError` 발생 시 저장 후 안전 종료
- 상태 파일이 없거나 손상된 경우 기본 데이터로 복구

## 파일 구조

```text
.
├── main.py       # 프로그램 시작점
├── quiz.py       # Quiz 클래스와 기본 퀴즈
├── game.py       # QuizGame 클래스, 메뉴와 게임 흐름
├── storage.py    # state.json 읽기·쓰기·복구
├── state.json    # 문제, 최고 점수, 게임 기록
├── tests/
│   └── test_quiz_game.py
└── docs/superpowers/
    ├── specs/
    └── plans/
```

## 클래스 역할

`Quiz`는 문제, 4개 선택지, 정답 번호, 힌트를 하나의 객체로 묶습니다. `QuizGame`은 여러 `Quiz` 객체를 관리하고, 메뉴·입력·채점·보너스 기능을 실행합니다. 저장 책임은 `storage.py` 함수로 분리해 게임 흐름과 JSON 형식 검사를 나누었습니다.

주요 공개 메서드는 다음과 같습니다.

| 클래스 | 메서드 | 역할 |
|---|---|---|
| `Quiz` | `display()` | 문제와 선택지를 문자열로 표시 |
| `Quiz` | `is_correct(choice)` | 정답 여부 판정 |
| `Quiz` | `to_dict()` / `from_dict()` | JSON 데이터 변환 |
| `QuizGame` | `run()` | 메뉴와 안전 종료 흐름 실행 |
| `QuizGame` | `play_quiz(quizzes, count)` | 랜덤 출제·힌트·채점·기록 |
| `QuizGame` | `add_quiz()` / `delete_quiz()` | 문제 추가·삭제 및 저장 |
| `QuizGame` | `list_quizzes()` / `show_scores()` | 문제 목록·점수 표시 |

## state.json 설명

파일은 프로젝트 루트에 UTF-8로 저장됩니다.

```json
{
  "quizzes": [{"question": "...", "choices": ["..."], "answer": 1, "hint": "..."}],
  "best_score": 0,
  "history": [{
    "timestamp": "2026-11-07T12:00:00",
    "question_count": 3,
    "correct": 2,
    "hints": 1,
    "score": 1
  }]
}
```

첫 실행에서 파일이 없으면 기본 6문제를 사용합니다. JSON을 읽을 수 없거나 `quizzes`, `best_score`, `history` 구조가 올바르지 않으면 기본 상태로 복구합니다. 프로그램을 종료하거나 문제·점수 기록을 변경할 때 현재 상태를 저장합니다.

### 손상 파일 백업과 저장 안정성

손상된 `state.json`을 발견하면 덮어쓰기 전에 `state.corrupt-YYYYMMDD-HHMMSS-microseconds.json` 형식의 snapshot을 같은 폴더에 남기고 기본 상태로 복구합니다. 백업 성공 여부는 콘솔에 안내합니다. 정상 저장은 먼저 `state.tmp-<uuid>.json`에 기록한 뒤 `os.replace()`로 교체하므로, 저장 중 중단될 때 기존 파일이 부분적으로 덮어써질 위험을 줄입니다. 저장 자체가 실패하면 기존 파일을 보존하고 게임 화면에 오류를 알립니다.

### JSON 저장 방식의 한계

현재 방식은 매번 전체 상태를 메모리에서 읽고 전체 JSON 파일을 다시 쓰므로, 퀴즈와 기록이 매우 많아지면 파일 크기·메모리 사용량·저장 시간이 함께 증가합니다. 여러 프로세스가 동시에 쓰면 마지막 저장이 앞선 저장을 덮어쓸 수 있고, 조건 검색이나 부분 갱신도 어렵습니다. 규모가 커지면 SQLite를 사용해 기록 테이블을 분리하고, 트랜잭션과 인덱스로 부분 조회·갱신을 지원하는 방향을 고려할 수 있습니다.

## 테스트

`tests/test_quiz_game.py`는 문제 검증과 JSON 변환, 기본 데이터 6문제, 손상 파일 복구, 메뉴 흐름, 입력 재시도, 안전 종료, 문제 추가·목록·삭제, 랜덤 출제, 힌트 감점, 점수 이력을 확인합니다.

## Git 실습 및 증빙

기능 단위로 커밋하고 `bonus-features` 브랜치에서 보너스를 구현한 뒤 `master`에 병합했습니다. 원격 저장소는 다음과 같습니다.

https://github.com/ttoli54/python-quiz-game

최종 커밋 그래프와 원격 상태는 다음 명령으로 확인합니다.

```powershell
git log --oneline --graph --all
git remote -v
```

로컬 `master` 브랜치를 원격 `main` 브랜치에 업로드했고, 원격 저장소의 초기 README 커밋과도 병합했습니다. 별도 폴더 clone → 변경·commit·push → 원본 pull 실습의 실제 출력은 `docs/git-evidence.txt`에 기록합니다.
