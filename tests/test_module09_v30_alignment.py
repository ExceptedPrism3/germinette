"""Regression tests for Module 09 v3.0 checker alignment."""

from __future__ import annotations

from pathlib import Path
import textwrap

import pytest


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def test_module09_ex1_requires_model_validator_not_validator(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_09 import Tester

    _write(
        tmp_path / "ex1" / "alien_contact.py",
        """
        from datetime import datetime
        from enum import Enum
        from pydantic import BaseModel, validator


        class ContactType(Enum):
            radio = "radio"
            telepathic = "telepathic"
            physical = "physical"
            visual = "visual"


        class AlienContact(BaseModel):
            contact_id: str
            timestamp: datetime
            location: str
            contact_type: ContactType
            signal_strength: float
            duration_minutes: int
            witness_count: int
            is_verified: bool = False

            @validator("contact_id")
            def bad_v1(cls: object, v: str) -> str:
                return v
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_alien_contact()
    errors = "\n".join(tester.grouped_errors.get("Exercise 1", []))
    assert "Deprecated @validator" in errors


def test_module09_structure_check_flags_missing_ex_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_09 import Tester

    _write(tmp_path / "ex0" / "space_station.py", "print('ok')\n")
    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.run()
    errors = "\n".join(tester.grouped_errors.get("Project Structure", []))
    assert "Missing Exercise Files" in errors
    assert "ex1/alien_contact.py" in errors
    assert "ex2/space_crew.py" in errors
