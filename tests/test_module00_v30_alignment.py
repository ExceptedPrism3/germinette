"""Regression tests for Module 00 v3.0 checker structure rules."""

from __future__ import annotations

from pathlib import Path
import textwrap

import pytest


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def test_module00_rejects_main_block(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from germinette.subjects.python_module_00 import Tester

    _write(
        tmp_path / "ex0" / "ft_hello_garden.py",
        """
        def ft_hello_garden() -> None:
            print("Hello, Garden Community!")

        if __name__ == "__main__":
            ft_hello_garden()
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_hello_garden()
    errors = "\n".join(tester.grouped_errors.get("Exercise 0", []))
    assert "__main__ block" in errors


def test_module00_allows_recursive_helper(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from germinette.subjects.python_module_00 import Tester

    _write(
        tmp_path / "ex6" / "ft_count_harvest_recursive.py",
        """
        def _helper(day: int, total: int) -> None:
            if day > total:
                print("Harvest time!")
                return
            print(f"Day {day}")
            _helper(day + 1, total)

        def ft_count_harvest_recursive() -> None:
            total = int(input("Days until harvest: "))
            _helper(1, total)
        """,
    )
    _write(
        tmp_path / "ex6" / "ft_count_harvest_iterative.py",
        """
        def ft_count_harvest_iterative() -> None:
            total = int(input("Days until harvest: "))
            for day in range(1, total + 1):
                print(f"Day {day}")
            print("Harvest time!")
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_count_harvest()
    errors = "\n".join(tester.grouped_errors.get("Exercise 6", []))
    assert "__main__ block" not in errors
    assert "Unexpected function" not in errors
