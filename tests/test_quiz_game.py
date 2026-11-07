import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class QuizTests(unittest.TestCase):
    def test_quiz_checks_answers_and_round_trips_to_json(self):
        from quiz import Quiz

        quiz = Quiz("봉준호 감독의 영화는?", ["기생충", "타짜", "곡성", "부산행"], 1, "아카데미 작품상 수상작")

        self.assertTrue(quiz.is_correct(1))
        self.assertFalse(quiz.is_correct(2))
        self.assertEqual(Quiz.from_dict(quiz.to_dict()).hint, "아카데미 작품상 수상작")

    def test_quiz_requires_four_choices_and_valid_answer(self):
        from quiz import Quiz

        with self.assertRaises(ValueError):
            Quiz("문제", ["하나", "둘"], 1)
        with self.assertRaises(ValueError):
            Quiz("문제", ["하나", "둘", "셋", "넷"], 5)


class DefaultQuizTests(unittest.TestCase):
    def test_default_quizzes_have_at_least_six_valid_questions(self):
        from quiz import Quiz, default_quizzes

        quizzes = default_quizzes()

        self.assertGreaterEqual(len(quizzes), 6)
        self.assertTrue(all(isinstance(item, Quiz) for item in quizzes))
        self.assertTrue(all(len(item.choices) == 4 for item in quizzes))
        self.assertEqual(len({item.question for item in quizzes}), len(quizzes))


class StorageTests(unittest.TestCase):
    def test_missing_file_returns_default_state(self):
        from storage import load_state

        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            state = load_state(Path(folder) / "state.json")

        self.assertGreaterEqual(len(state["quizzes"]), 6)
        self.assertEqual(state["best_score"], 0)
        self.assertEqual(state["history"], [])

    def test_valid_state_round_trips_and_corrupt_state_recovers(self):
        from storage import load_state, save_state

        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            path = Path(folder) / "state.json"
            state = {"quizzes": [], "best_score": 4, "history": [{"score": 4}]}
            save_state(path, state)
            self.assertEqual(load_state(path), state)
            path.write_text("{not json", encoding="utf-8")
            recovered = load_state(path)

        self.assertGreaterEqual(len(recovered["quizzes"]), 6)
        self.assertEqual(recovered["best_score"], 0)

    def test_state_missing_required_key_recovers(self):
        from storage import load_state

        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            path = Path(folder) / "state.json"
            path.write_text(json.dumps({"quizzes": []}), encoding="utf-8")
            state = load_state(path)

        self.assertGreaterEqual(len(state["quizzes"]), 6)
        self.assertIn("history", state)


class GameFlowTests(unittest.TestCase):
    def test_play_quiz_returns_score_summary(self):
        from game import QuizGame
        from quiz import Quiz

        answers = iter(["n", "1", "n", "2"])
        quizzes = [
            Quiz("첫 문제", ["정답", "오답", "오답", "오답"], 1),
            Quiz("둘째 문제", ["오답", "정답", "오답", "오답"], 2),
        ]

        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            game = QuizGame(Path(folder) / "state.json", input_fn=lambda _: next(answers), output_fn=lambda _: None)
            with patch("game.random.sample", return_value=quizzes):
                result = game.play_quiz(quizzes, 2)

        self.assertEqual(result["correct"], 2)
        self.assertEqual(result["score"], 2)
        self.assertEqual(result["question_count"], 2)

    def test_run_exit_saves_state(self):
        from game import QuizGame

        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            path = Path(folder) / "state.json"
            output = []
            game = QuizGame(path, input_fn=lambda _: "6", output_fn=output.append)
            game.run()

            self.assertTrue(path.exists())
            self.assertTrue(any("종료" in line for line in output))


class InputTests(unittest.TestCase):
    def test_read_int_retries_after_blank_text_invalid_text_and_range(self):
        from game import read_int

        answers = iter(["", "abc", "0", "6", " 2 "])
        output = []

        result = read_int("번호: ", 1, 5, input_fn=lambda _: next(answers), output_fn=output.append)

        self.assertEqual(result, 2)
        self.assertEqual(len(output), 4)

    def test_run_saves_and_returns_on_eof(self):
        from game import QuizGame

        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            path = Path(folder) / "state.json"
            output = []

            def eof(_):
                raise EOFError

            QuizGame(path, input_fn=eof, output_fn=output.append).run()

            self.assertTrue(path.exists())
            self.assertTrue(any("안전하게" in line for line in output))


class ManagementTests(unittest.TestCase):
    def test_add_quiz_rejects_blank_question_and_saves_valid_quiz(self):
        from game import QuizGame
        from storage import load_state

        answers = iter(["", "새로운 문제", "첫 보기", "둘째 보기", "셋째 보기", "넷째 보기", "2", "힌트"])
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            path = Path(folder) / "state.json"
            output = []
            game = QuizGame(path, input_fn=lambda _: next(answers), output_fn=output.append)

            game.add_quiz()
            saved = load_state(path)

        self.assertEqual(game.quizzes[-1].question, "새로운 문제")
        self.assertEqual(saved["quizzes"][-1]["answer"], 2)
        self.assertTrue(any("비어 있을 수 없습니다" in line for line in output))

    def test_list_quizzes_prints_questions(self):
        from game import QuizGame

        output = []
        game = QuizGame(Path("unused.json"), input_fn=lambda _: "5", output_fn=output.append)

        game.list_quizzes()

        self.assertTrue(any("등록된 퀴즈" in line for line in output))
        self.assertTrue(any("기생충" in line for line in output))

    def test_show_scores_handles_empty_history(self):
        from game import QuizGame

        output = []
        game = QuizGame(Path("unused.json"), input_fn=lambda _: "5", output_fn=output.append)

        game.show_scores()

        self.assertTrue(any("아직 게임 기록이 없습니다" in line for line in output))


class BonusTests(unittest.TestCase):
    def _quizzes(self):
        from quiz import Quiz

        return [
            Quiz("첫 문제", ["정답", "오답", "오답", "오답"], 1, "첫 힌트"),
            Quiz("둘째 문제", ["오답", "정답", "오답", "오답"], 2, "둘째 힌트"),
        ]

    def test_play_quiz_uses_random_sample_without_changing_saved_order(self):
        from game import QuizGame

        quizzes = self._quizzes()
        answers = iter(["n", "1", "n", "2"])
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            game = QuizGame(Path(folder) / "state.json", input_fn=lambda _: next(answers), output_fn=lambda _: None)
            with patch("game.random.sample", return_value=[quizzes[1], quizzes[0]]):
                result = game.play_quiz(quizzes, 2)

        self.assertEqual(result["question_count"], 2)
        self.assertEqual([quiz.question for quiz in quizzes], ["첫 문제", "둘째 문제"])

    def test_hint_reduces_score_but_never_below_zero_and_records_history(self):
        from game import QuizGame

        answers = iter(["y", "1", "y", "2"])
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            game = QuizGame(Path(folder) / "state.json", input_fn=lambda _: next(answers), output_fn=lambda _: None)
            result = game.play_quiz(self._quizzes(), 2)

        self.assertEqual(result["hints"], 2)
        self.assertEqual(result["score"], 0)
        self.assertEqual(len(game.history), 1)
        self.assertIn("timestamp", game.history[0])

    def test_question_count_is_bounded(self):
        from game import QuizGame

        answers = iter(["0", "3", "2"])
        output = []
        game = QuizGame(Path("unused.json"), input_fn=lambda _: next(answers), output_fn=output.append)
        game.quizzes = self._quizzes()

        count = game.ask_question_count()

        self.assertEqual(count, 2)
        self.assertTrue(any("1-2" in line for line in output))

    def test_delete_quiz_persists_and_empty_delete_is_safe(self):
        from game import QuizGame
        from storage import load_state

        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            path = Path(folder) / "state.json"
            answers = iter(["1"])
            game = QuizGame(path, input_fn=lambda _: next(answers), output_fn=lambda _: None)
            original_first = game.quizzes[0].question
            game.delete_quiz()
            saved = load_state(path)

            self.assertNotEqual(saved["quizzes"][0]["question"], original_first)
            game.quizzes.clear()
            game.delete_quiz()


class MenuTests(unittest.TestCase):
    def test_bonus_menu_lists_delete_and_exit_once(self):
        from game import QuizGame

        output = []
        QuizGame(Path("unused.json"), input_fn=lambda _: "6", output_fn=output.append).run()

        menu_text = "\n".join(output)
        self.assertEqual(menu_text.count("5."), 1)
        self.assertIn("5. 퀴즈 삭제", menu_text)
        self.assertIn("6. 종료", menu_text)


class ProjectSkeletonTests(unittest.TestCase):
    def test_modules_are_importable(self):
        import game  # noqa: F401
        import quiz  # noqa: F401
        import storage  # noqa: F401


if __name__ == "__main__":
    unittest.main()
