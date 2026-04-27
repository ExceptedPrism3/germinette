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
