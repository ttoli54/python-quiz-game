"""Application entry point."""

from pathlib import Path
from typing import Callable

from game import QuizGame


def main(
    state_path: Path | None = None,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> None:
    path = state_path or Path(__file__).with_name("state.json")
    QuizGame(path, input_fn=input_fn, output_fn=output_fn).run()


if __name__ == "__main__":
    main()
