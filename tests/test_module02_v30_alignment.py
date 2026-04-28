"""Regression tests for Module 02 v3.0 checker behavior."""

from __future__ import annotations

from pathlib import Path
import textwrap

import pytest


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def test_module02_ex0_requires_try_except_in_test_function(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_02 import Tester

    _write(
        tmp_path / "ex0" / "ft_first_exception.py",
        """
        def input_temperature(temp_str: str) -> int:
            return int(temp_str)


        def test_temperature() -> None:
            print(input_temperature("25"))
            print(input_temperature("abc"))


        if __name__ == "__main__":
            test_temperature()
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_first_exception()
    errors = "\n".join(tester.grouped_errors.get("Exercise 0", []))
    assert "MUST use 'try/except' blocks" in errors


def test_module02_ex2_requires_multi_exception_except(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_02 import Tester

    _write(
        tmp_path / "ex2" / "ft_different_errors.py",
        """
        def garden_operations(operation_number: int) -> None:
            if operation_number == 0:
                int("abc")
            elif operation_number == 1:
                _ = 1 / 0
            elif operation_number == 2:
                open("/non/existent/file", "r", encoding="utf-8")
            elif operation_number == 3:
                _ = "a" + 1  # type: ignore[operator]
            else:
                return


        def test_error_types() -> None:
            i = 0
            while i < 5:
                try:
                    garden_operations(i)
                except Exception as e:
                    print(f"caught {e}")
                i = i + 1
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_different_errors()
    errors = "\n".join(tester.grouped_errors.get("Exercise 2", []))
    assert "catching multiple exception types together" in errors
