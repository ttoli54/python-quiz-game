import json
import tempfile
import unittest
from pathlib import Path


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


class ProjectSkeletonTests(unittest.TestCase):
    def test_modules_are_importable(self):
        import game  # noqa: F401
        import quiz  # noqa: F401
        import storage  # noqa: F401


if __name__ == "__main__":
    unittest.main()
