"""
Integration test: Module 07 tester against a golden reference project.

Run from repository root (use the venv's interpreter so Conda does not shadow ``python``):

    python3 -m pip install -e ".[dev]"
    python3 -m pytest tests/test_integration_module07.py -v
    # or: .venv/bin/python -m pytest tests/test_integration_module07.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
GOLDEN_ROOT = REPO_ROOT / "tests" / "fixtures" / "python_module_07_golden"


@pytest.fixture
def golden_cwd(monkeypatch: pytest.MonkeyPatch) -> None:
    """Run with CWD = golden tree; import germinette from repo root."""
    monkeypatch.chdir(GOLDEN_ROOT)
    root = str(REPO_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def test_module_07_golden_full_run_no_errors(golden_cwd: None) -> None:
    """Golden ex0–ex4 must pass flake8, type hints, strict checks, and output."""
    from germinette.subjects.python_module_07 import Tester

    tester = Tester()
    tester.run()
    assert not tester.grouped_errors, (
        "Module 07 golden project should pass all checks; got:\n"
        f"{tester.grouped_errors}"
    )


def test_module_07_golden_exercises_individually(golden_cwd: None) -> None:
    """Each exercise entrypoint should pass in isolation."""
    from germinette.subjects.python_module_07 import Tester

    for name, _ in Tester().exercises:
        tester = Tester()
        tester.run(exercise_name=name)
        assert not tester.grouped_errors, (
            f"Exercise {name} failed: {tester.grouped_errors}"
        )
