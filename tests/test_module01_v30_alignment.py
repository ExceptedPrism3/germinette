"""Regression tests for Module 01 v3.0 checker behavior."""

from __future__ import annotations

from pathlib import Path
import textwrap

import pytest


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def test_module01_ex0_requires_main_guard(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_01 import Tester

    _write(
        tmp_path / "ex0" / "ft_garden_intro.py",
        """
        def banner() -> None:
            print("=== Welcome to My Garden ===")
            print("Plant: Rose")
            print("Height: 25cm")
            print("Age: 30 days")
            print("=== End of Program ===")
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_garden_intro()
    errors = "\n".join(tester.grouped_errors.get("Exercise 0", []))
    assert "Missing Pattern" in errors
    assert "__main__" in errors


def test_module01_ex1_requires_show_method(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_01 import Tester

    _write(
        tmp_path / "ex1" / "ft_garden_data.py",
        """
        class Plant:
            def __init__(self, name: str, height: float, age: int) -> None:
                self.name = name
                self.height = height
                self.age = age


        if __name__ == "__main__":
            p = Plant("Rose", 25.0, 30)
            print(f"{p.name}: {p.height}cm, {p.age} days old")
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_garden_data()
    errors = "\n".join(tester.grouped_errors.get("Exercise 1", []))
    assert "Missing Method" in errors
    assert "show" in errors
