"""Application entry point."""

from pathlib import Path

from game import QuizGame


if __name__ == "__main__":
    QuizGame(Path(__file__).with_name("state.json")).run()
