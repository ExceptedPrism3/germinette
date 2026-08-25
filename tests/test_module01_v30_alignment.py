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


def test_module01_ex1_allows_unparameterized_plant_instantiation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_01 import Tester

    _write(
        tmp_path / "ex1" / "ft_garden_data.py",
        """
        class Plant:
            name: str
            height: int
            age: int

            def show(self) -> None:
                print(f"{self.name}: {self.height}cm, {self.age} days old")


        if __name__ == "__main__":
            p1 = Plant()
            p1.name = "Rose"
            p1.height = 25
            p1.age = 30
            p1.show()

            p2 = Plant()
            p2.name = "Sunflower"
            p2.height = 80
            p2.age = 45
            p2.show()

            p3 = Plant()
            p3.name = "Cactus"
            p3.height = 15
            p3.age = 120
            p3.show()
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_garden_data()
    errors = tester.grouped_errors.get("Exercise 1", [])
    assert not errors, f"Exercise 1 failed with errors: {errors}"


def test_module01_ex2_allows_unparameterized_plant_instantiation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_01 import Tester

    _write(
        tmp_path / "ex2" / "ft_plant_growth.py",
        """
        class Plant:
            name: str
            height: int
            plant_age: int

            def grow(self) -> None:
                self.height += 2

            def age(self) -> None:
                self.plant_age += 1

            def show(self) -> None:
                print(f"{self.name}: {self.height}cm, {self.plant_age} days old")


        if __name__ == "__main__":
            p = Plant()
            p.name = "Bamboo"
            p.height = 100
            p.plant_age = 10
            for day in range(1, 8):
                print(f"=== Day {day} ===")
                p.show()
                p.grow()
                p.age()
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_plant_growth()
    errors = tester.grouped_errors.get("Exercise 2", [])
    assert not errors, f"Exercise 2 failed with errors: {errors}"
