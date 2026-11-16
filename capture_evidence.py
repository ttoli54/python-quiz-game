"""Capture reproducible CLI evidence for the Korean movie quiz game."""

from __future__ import annotations

import html
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EVIDENCE_DIR = ROOT / "docs" / "evidence"


def run_command(args: list[str], input_text: str = "") -> str:
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        args,
        cwd=ROOT,
        input=input_text,
        text=True,
        encoding="utf-8",
        capture_output=True,
        env=environment,
        check=False,
    )
    output = result.stdout
    if result.stderr:
        output += f"\n[stderr]\n{result.stderr}"
    output = "\n".join(line.rstrip() for line in output.splitlines())
    return f"{output}\n\n[exit code: {result.returncode}]"


def write_terminal_page(filename: str, title: str, command: str, output: str) -> None:
    page = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>
body {{ margin: 0; background: #111827; color: #e5e7eb; font-family: Consolas, 'Malgun Gothic', monospace; }}
main {{ margin: 32px; background: #0b1220; border: 2px solid #334155; border-radius: 14px; padding: 28px; }}
h1 {{ color: #cbd5e1; font-size: 24px; margin: 0 0 22px; }}
.command {{ color: #93c5fd; margin-bottom: 18px; }}
pre {{ white-space: pre; font-size: 17px; line-height: 1.55; margin: 0; }}
</style></head><body><main>
<h1>{html.escape(title)}</h1>
<div class="command">PS&gt; {html.escape(command)}</div>
<pre>{html.escape(output)}</pre>
</main></body></html>"""
    (EVIDENCE_DIR / filename).write_text(page, encoding="utf-8")
    (EVIDENCE_DIR / filename.replace(".html", ".txt")).write_text(
        f"실행 명령: {command}\n\n{output}", encoding="utf-8"
    )


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT) as folder:
        state_path = Path(folder) / "demo-state.json"
        game_code = (
            "import random; from pathlib import Path; from main import main; "
            f"random.seed(7); main(Path(r'{state_path}'))"
        )
        game_input = "\n".join(["1", "2", "y", "3", "n", "1", "6"]) + "\n"
        write_terminal_page(
            "hint-random-run.html",
            "한국 영화 퀴즈 - 랜덤 출제와 힌트 감점",
            "random.seed(7) | python -c ...",
            run_command([sys.executable, "-c", game_code], game_input),
        )

    write_terminal_page(
        "unittest-run.html",
        "한국 영화 퀴즈 - unit tests",
        "python -m unittest -v",
        run_command([sys.executable, "-m", "unittest", "-v"]),
    )
    print("HTML/TXT evidence pages written to docs/evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
