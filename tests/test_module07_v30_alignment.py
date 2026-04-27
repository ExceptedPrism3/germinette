"""Regression tests for Module 07 v3.0 checker alignment."""

from __future__ import annotations

from pathlib import Path
import textwrap

import pytest


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def test_module07_rejects_external_imports(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_07 import Tester

    # Minimal directory skeleton expected by tester.
    _write(tmp_path / "ex0" / "__init__.py", "")
    _write(tmp_path / "ex1" / "__init__.py", "")
    _write(tmp_path / "ex2" / "__init__.py", "")
    _write(
        tmp_path / "battle.py",
        """
        import json

        print("Testing factory")
        print(json.dumps({"probe": 1}))
        print("Flameling is a Fire type Creature")
        print("Pyrodon is a Fire/Flying type Creature")
        print("Aquabub is a Water type Creature")
        print("Torragon is a Water type Creature")
        print("Testing battle")
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_creature_factory()
    errors = "\n".join(tester.grouped_errors.get("Exercise 0", []))
    assert "Forbidden Import" in errors
    assert "json" in errors


def test_module07_requires_init_in_each_ex_folder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_07 import Tester

    _write(tmp_path / "battle.py", "print('ok')\n")
    _write(tmp_path / "capacitor.py", "print('ok')\n")
    _write(tmp_path / "tournament.py", "print('ok')\n")
    # Deliberately incomplete exercise package setup.
    _write(tmp_path / "ex0" / "__init__.py", "")

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.run()
    errors = "\n".join(tester.grouped_errors.get("Project Structure", []))
    assert "Missing Package Files" in errors
    assert "ex1/__init__.py" in errors
    assert "ex2/__init__.py" in errors
