# 한국 영화 퀴즈 게임 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기본 콘솔 퀴즈 과제와 다섯 가지 보너스 기능을 실제로 실행·저장·검증할 수 있는 Python 프로젝트를 만든다.

**Architecture:** `Quiz`는 문제 하나의 데이터와 채점을 담당하고, `storage.py`는 `state.json`의 읽기·쓰기와 복구를 담당한다. `QuizGame`은 입력·메뉴·게임 흐름·보너스를 관리하며 `main.py`는 실행 진입점만 제공한다.

**Tech Stack:** Python 3.10+, 표준 라이브러리(`json`, `random`, `datetime`, `unittest`), Git.

**Spec:** `docs/superpowers/specs/2026-11-07-python-quiz-game-design.md`

## Global Constraints

- Python 3.10 이상을 사용한다.
- 외부 라이브러리 없이 기본 문법과 표준 라이브러리만 사용한다.
- 데이터 파일은 프로젝트 루트의 `state.json`이며 UTF-8로 읽고 쓴다.
- 문제는 4개의 선택지와 1~4 범위의 정답을 가진다.
- 빈 입력, 숫자 변환 실패, 허용 범위 밖 숫자, `KeyboardInterrupt`, `EOFError`를 안전하게 처리한다.
- 손상되거나 없는 상태 파일은 기본 문제 데이터로 복구한다.
- 실제로 확인하지 않은 테스트·Git·GitHub 결과를 README에 적지 않는다.

## Review Focus

- 손상된 JSON과 필수 키 누락: 기본 상태로 복구하고 프로그램은 계속 실행되어야 한다. `test_corrupt_state_falls_back_to_defaults`.
- 숫자 입력의 공백·문자·범위 오류: 재입력 가능한 검증 결과를 내야 한다. `test_parse_choice_rejects_invalid_values`.
- 힌트 감점과 0점 하한: 힌트 사용 후에도 점수가 음수가 되면 안 된다. `test_score_never_goes_below_zero`.
- 문제 수가 전체 문제보다 큰 선택: 가능한 문제 수 범위로 재입력시켜야 한다. `test_question_count_is_bounded`.
- 빈 목록에서 삭제·플레이: 오류 없이 안내하고 상태를 유지해야 한다. `test_empty_quiz_actions_are_safe`.

---

### Task 1: Project skeleton and test helpers

**Files:**
- Create: `.gitignore`
- Create: `tests/__init__.py`
- Create: `tests/test_quiz_game.py`
- Create: `README.md` (initial project outline)

**Interfaces:**
- Produces: test module with `unittest` helpers and a temporary-state factory for later tasks.

- [ ] **Step 1: Write the initial failing import test**

Add `test_modules_are_importable` that imports `quiz`, `storage`, and `game`.

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest -v`
Expected: import failure because implementation modules do not exist yet.

- [ ] **Step 3: Add project metadata files and empty module files**

Create the initial files and a README outline; module files may contain only docstrings until their tasks implement behavior.

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m unittest -v`
Expected: the import test passes.

- [ ] **Step 5: Commit**

```powershell
git add .
git commit -m "chore: initialize quiz game project"
```

### Task 2: Quiz model and validation

**Files:**
- Modify: `quiz.py`
- Modify: `tests/test_quiz_game.py`

**Interfaces:**
- Produces: `Quiz(question, choices, answer, hint="")`, `display() -> str`, `is_correct(choice: int) -> bool`, `to_dict() -> dict`, and `Quiz.from_dict(data: dict) -> Quiz`.

- [ ] **Step 1: Write failing tests**

Test four-choice validation, correct/incorrect answers, and JSON round-trip including `hint`.

- [ ] **Step 2: Run targeted tests and verify failure**

Run: `python -m unittest -v tests.test_quiz_game.QuizTests`
Expected: failures because `Quiz` behavior is not implemented.

- [ ] **Step 3: Implement `Quiz`**

Validate non-empty question, exactly four choices, non-empty choices, and answer in 1..4. Store the answer as an integer.

- [ ] **Step 4: Run targeted tests and verify pass**

Expected: all `QuizTests` pass.

- [ ] **Step 5: Commit**

```powershell
git add quiz.py tests/test_quiz_game.py
git commit -m "feat: add quiz model and validation"
```

### Task 3: Default Korean movie quiz data

**Files:**
- Modify: `quiz.py`
- Modify: `tests/test_quiz_game.py`

**Interfaces:**
- Produces: `default_quizzes() -> list[Quiz]` returning at least six distinct Korean movie questions.

- [ ] **Step 1: Write failing tests**

Test that `default_quizzes()` returns at least six `Quiz` objects with four choices and valid answers.

- [ ] **Step 2: Run targeted tests and verify failure**

Run: `python -m unittest -v tests.test_quiz_game.DefaultQuizTests`
Expected: failure because the default data function does not exist.

- [ ] **Step 3: Implement six Korean movie questions**

Use clear Korean text, one unambiguous answer per question, and a useful hint for each.

- [ ] **Step 4: Run targeted tests and verify pass**

Expected: all default-data tests pass.

- [ ] **Step 5: Commit**

```powershell
git add quiz.py tests/test_quiz_game.py
git commit -m "feat: add Korean movie quiz dataset"
```

### Task 4: JSON storage and recovery

**Files:**
- Modify: `storage.py`
- Modify: `tests/test_quiz_game.py`

**Interfaces:**
- Produces: `load_state(path: Path) -> dict`, `save_state(path: Path, state: dict) -> None`, and `default_state() -> dict`.

- [ ] **Step 1: Write failing tests**

Test missing-file defaults, valid save/load, corrupted JSON fallback, and required-key fallback.

- [ ] **Step 2: Run targeted tests and verify failure**

Run: `python -m unittest -v tests.test_quiz_game.StorageTests`
Expected: failures because storage functions are not implemented.

- [ ] **Step 3: Implement storage**

Use UTF-8 JSON with `ensure_ascii=False`, convert default `Quiz` objects through `to_dict()`, and return a fresh default state on read errors or invalid schema.

- [ ] **Step 4: Run targeted tests and verify pass**

Expected: all storage tests pass.

- [ ] **Step 5: Commit**

```powershell
git add storage.py tests/test_quiz_game.py
git commit -m "feat: persist quiz state in JSON"
```

### Task 5: Basic game menu and play flow

**Files:**
- Modify: `game.py`
- Create: `main.py`
- Modify: `tests/test_quiz_game.py`

**Interfaces:**
- Produces: `QuizGame(state_path: Path, input_fn=input, output_fn=print)`, `play_quiz(quizzes: list[Quiz], count: int) -> dict`, and `run() -> None`.

- [ ] **Step 1: Write failing tests**

Test a deterministic play session with injected input, score calculation, menu rendering, and state save on exit.

- [ ] **Step 2: Run targeted tests and verify failure**

Run: `python -m unittest -v tests.test_quiz_game.GameFlowTests`
Expected: failures because `QuizGame` is not implemented.

- [ ] **Step 3: Implement the basic game**

Load state in the constructor, show five menu options, print a quiz, collect valid answers, update `best_score`, and save on normal exit.

- [ ] **Step 4: Run targeted tests and verify pass**

Expected: all basic flow tests pass.

- [ ] **Step 5: Commit**

```powershell
git add game.py main.py tests/test_quiz_game.py
git commit -m "feat: implement basic quiz game flow"
```

### Task 6: Input validation and safe interruption

**Files:**
- Modify: `game.py`
- Modify: `tests/test_quiz_game.py`

**Interfaces:**
- Produces: `read_int(prompt: str, minimum: int, maximum: int) -> int` and safe handling for `KeyboardInterrupt`/`EOFError` in `run()`.

- [ ] **Step 1: Write failing tests**

Test whitespace trimming, blank input, non-numeric input, out-of-range input, and safe interruption with a fake input function.

- [ ] **Step 2: Run targeted tests and verify failure**

Run: `python -m unittest -v tests.test_quiz_game.InputTests`
Expected: failures for invalid-input behavior.

- [ ] **Step 3: Implement shared input validation**

Keep prompting until a valid integer is returned; convert interruption into a short message and let `run()` save before returning.

- [ ] **Step 4: Run targeted tests and verify pass**

Expected: all input tests pass.

- [ ] **Step 5: Commit**

```powershell
git add game.py tests/test_quiz_game.py
git commit -m "fix: handle invalid input and safe exits"
```

### Task 7: Add, list, and score screens

**Files:**
- Modify: `game.py`
- Modify: `tests/test_quiz_game.py`

**Interfaces:**
- Produces: `add_quiz()`, `list_quizzes()`, and `show_scores()` methods used by the menu.

- [ ] **Step 1: Write failing tests**

Test adding a valid question, rejecting blank fields, listing saved questions, and showing “no games yet” when history is empty.

- [ ] **Step 2: Run targeted tests and verify failure**

Run: `python -m unittest -v tests.test_quiz_game.ManagementTests`
Expected: failures because management methods are not implemented.

- [ ] **Step 3: Implement management screens**

Collect question, four choices, answer, and hint; append a `Quiz`; save immediately after mutation; show list and best score/history summaries.

- [ ] **Step 4: Run targeted tests and verify pass**

Expected: all management tests pass.

- [ ] **Step 5: Commit**

```powershell
git add game.py tests/test_quiz_game.py
git commit -m "feat: add quiz management and score screens"
```

### Task 8: Bonus features on a feature branch

**Files:**
- Modify: `game.py`
- Modify: `tests/test_quiz_game.py`

**Interfaces:**
- Produces: randomized selection, requested question count, hint use with score deduction, quiz deletion, and history entries with timestamp/questions/correct/hints/score.

- [ ] **Step 1: Create the feature branch**

Run: `git checkout -b bonus-features`.

- [ ] **Step 2: Write failing tests**

Test bounded question counts, randomized selection via a patched random source, hint scoring, deletion persistence, and history record shape.

- [ ] **Step 3: Run targeted tests and verify failure**

Run: `python -m unittest -v tests.test_quiz_game.BonusTests`
Expected: failures for the bonus behaviors.

- [ ] **Step 4: Implement the bonus features**

Use `random.sample()` without mutating the saved quiz order. Let the play flow ask for count, optionally reveal a hint, apply the score rule from the design, append an ISO timestamped history record, and provide safe indexed deletion.

- [ ] **Step 5: Run targeted tests and verify pass**

Expected: all bonus tests pass.

- [ ] **Step 6: Commit**

```powershell
git add game.py tests/test_quiz_game.py
git commit -m "feat: add randomized quizzes hints deletion and history"
```

### Task 9: README, state file, and CLI polish

**Files:**
- Modify: `README.md`
- Modify: `main.py`
- Create: `state.json`
- Modify: `tests/test_quiz_game.py`

**Interfaces:**
- Produces: documented execution, file structure, data schema, bonus behavior, and a CLI smoke test that runs `main.py` with exit input.

- [ ] **Step 1: Write failing smoke test**

Test that `main.py` starts with a temporary working directory and exits cleanly when input is `5`.

- [ ] **Step 2: Run the smoke test and verify failure or missing documentation**

Run: `python -m unittest -v tests.test_quiz_game.CliSmokeTests`
Expected: the test identifies any remaining entry-point issue.

- [ ] **Step 3: Implement the entry point and README**

Make `main.py` resolve the project-root `state.json`, initialize defaults if needed, and document only verified commands and outcomes. Keep a UTF-8 sample state file with the six defaults and empty history.

- [ ] **Step 4: Run the full suite and CLI smoke test**

Run: `python -m unittest -v`
Expected: all tests pass.

- [ ] **Step 5: Commit**

```powershell
git add README.md main.py state.json tests/test_quiz_game.py
git commit -m "docs: document quiz game and CLI usage"
```

### Task 10: Merge the bonus branch and verify Git history

**Files:**
- Git metadata only; no source changes required unless verification exposes an issue.

**Interfaces:**
- Produces: `main` containing the bonus feature merge and a verified graph of meaningful commits.

- [ ] **Step 1: Run full verification on `bonus-features`**

Run: `python -m unittest -v` and `python main.py` with a scripted exit input.
Expected: all tests pass and the CLI exits without traceback.

- [ ] **Step 2: Merge into `main`**

Run: `git checkout master` followed by `git merge --no-ff bonus-features -m "merge: integrate bonus quiz features"`.
Expected: a merge commit is created without conflicts.

- [ ] **Step 3: Verify commit graph and required local commands**

Run: `git log --oneline --graph --all` and `git status --short --branch`.
Expected: at least ten meaningful commits, a visible bonus branch merge, and a clean working tree.

- [ ] **Step 4: Commit any verified final evidence updates**

Only if README needs actual outputs from verification, update it and commit with a specific message; never invent output.

### Task 11: Clone/pull practice and external handoff boundary

**Files:**
- Create outside the project: a temporary local clone folder, if a local bare remote is used for practice.
- Modify: `README.md` only with verified local or GitHub results.

**Interfaces:**
- Produces: evidence of clone and pull when a remote is available; otherwise a clearly documented external-action checklist.

- [ ] **Step 1: Check configured remotes and GitHub authorization**

Run: `git remote -v`.
Expected: use an existing authorized remote only if present; do not create or push to a new remote automatically.

- [ ] **Step 2: If a remote is authorized, clone and pull through a separate folder**

Perform the clone → separate README edit → commit → push → original-folder pull flow, verifying each command.

- [ ] **Step 3: If no remote is authorized, leave external steps for the user**

Document the exact commands and mark GitHub upload as pending rather than claiming it is complete.

- [ ] **Step 4: Run final verification**

Run: `python -m unittest -v`, `git status --short --branch`, and `git log --oneline --graph --all`.
Expected: tests pass; repository status and Git evidence are reported accurately.
