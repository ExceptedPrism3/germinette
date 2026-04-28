"""Regression tests for Module 06 v2.0 checker alignment."""

from __future__ import annotations

from pathlib import Path
import textwrap

import pytest


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def test_module06_rejects_non_project_imports(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_06 import Tester

    _write(
        tmp_path / "ft_alembic_0.py",
        """
        import json
        import elements

        print("=== Alembic 0 ===")
        print(json.dumps({"probe": 1}))
        print(elements.create_fire())
        """,
    )
    _write(
        tmp_path / "elements.py",
        """
        def create_fire() -> str:
            return "Fire element created"
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_alembic_0()
    errors = "\n".join(tester.grouped_errors.get("Alembic 0", []))
    assert "Forbidden Import" in errors
    assert "json" in errors


def test_module06_required_tree_check_flags_missing_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_06 import Tester

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    ok = tester.check_required_structure()
    assert ok is False
    errors = "\n".join(tester.grouped_errors.get("Project Structure", []))
    assert "Missing Mandatory Files" in errors


def test_module06_allows_intentional_alembic4_mypy_case(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_06 import Tester

    _write(
        tmp_path / "ft_alembic_4.py",
        """
        import alchemy

        print("=== Alembic 4 ===")
        print(f"Testing create_air: {alchemy.create_air()}")
        print("Testing the hidden create_earth:")
        print(alchemy.create_earth())
        """,
    )
    _write(
        tmp_path / "alchemy" / "__init__.py",
        """
        def create_air() -> str:
            return "Air element created"
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_alembic_4()
    errors = "\n".join(tester.grouped_errors.get("Alembic 4", []))
    assert "Style Error (Type Hints)" not in errors


def test_module06_transmutation_requires_absolute_and_relative_imports(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_06 import Tester

    _write(
        tmp_path / "ft_transmutation_0.py",
        """
        print("=== Transmutation 0 ===")
        print("Recipe transmuting Lead to Gold")
        """,
    )
    _write(
        tmp_path / "alchemy" / "transmutation" / "recipes.py",
        """
        import alchemy

        def lead_to_gold() -> str:
            return "Recipe transmuting Lead to Gold"
        """,
    )
    _write(tmp_path / "alchemy" / "__init__.py", "")
    _write(tmp_path / "alchemy" / "transmutation" / "__init__.py", "")

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_transmutation_0()
    errors = "\n".join(tester.grouped_errors.get("Transmutation 0", []))
    assert "absolute import and one relative import" in errors
