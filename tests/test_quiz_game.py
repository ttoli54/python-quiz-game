import unittest


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


class ProjectSkeletonTests(unittest.TestCase):
    def test_modules_are_importable(self):
        import game  # noqa: F401
        import quiz  # noqa: F401
        import storage  # noqa: F401


if __name__ == "__main__":
    unittest.main()
