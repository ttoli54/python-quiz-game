import unittest


class ProjectSkeletonTests(unittest.TestCase):
    def test_modules_are_importable(self):
        import game  # noqa: F401
        import quiz  # noqa: F401
        import storage  # noqa: F401


if __name__ == "__main__":
    unittest.main()
