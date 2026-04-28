"""Regression tests for A-Maze-ing checker subject alignment."""

from __future__ import annotations

from pathlib import Path

import pytest


def _write(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n", encoding="utf-8")


def test_amazeing_makefile_lint_requires_mypy_flags(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.a_maze_ing import Tester

    _write(
        tmp_path / "Makefile",
        """
        install:
        \tpython -m pip install -r requirements.txt

        run:
        \tpython a_maze_ing.py config.txt

        debug:
        \tpython -m pdb a_maze_ing.py config.txt

        clean:
        \trm -rf __pycache__ .mypy_cache

        lint:
        \tflake8 .
        \tmypy .
        """,
    )
    monkeypatch.chdir(tmp_path)

    tester = Tester()
    tester.test_makefile()
    errors = "\n".join(tester.grouped_errors.get("Makefile", []))
    assert "missing required mypy flags" in errors


def test_amazeing_requires_visible_42_pattern_on_large_mazes() -> None:
    from germinette.subjects.a_maze_ing import Tester

    tester = Tester()
    parsed = [[0x0 for _ in range(6)] for _ in range(6)]
    tester._check_42_pattern_requirement(
        parsed=parsed,
        width=6,
        height=6,
        runtime_output="",
        exercise_label="Run & Output",
    )
    errors = "\n".join(tester.grouped_errors.get("Run & Output", []))
    assert 'visible "42"' in errors


def test_amazeing_small_maze_requires_explanatory_message_for_42_omission() -> None:
    from germinette.subjects.a_maze_ing import Tester

    tester = Tester()
    parsed = [[0x0 for _ in range(4)] for _ in range(4)]
    tester._check_42_pattern_requirement(
        parsed=parsed,
        width=4,
        height=4,
        runtime_output="generation ok",
        exercise_label="Run & Output",
    )
    errors = "\n".join(tester.grouped_errors.get("Run & Output", []))
    assert "too small" in errors


def test_amazeing_small_maze_accepts_explanatory_message_for_42_omission() -> None:
    from germinette.subjects.a_maze_ing import Tester

    tester = Tester()
    parsed = [[0x0 for _ in range(4)] for _ in range(4)]
    tester._check_42_pattern_requirement(
        parsed=parsed,
        width=4,
        height=4,
        runtime_output='maze too small for "42" pattern',
        exercise_label="Run & Output",
    )
    assert not tester.grouped_errors.get("Run & Output")
