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


def test_module09_ex1_resolves_contact_type_even_when_members_are_uppercase(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Subject lists semantic tokens (radio …); PEP 436 style upper-case Enum names must work."""
    from germinette.subjects.python_module_09 import Tester

    _write(
        tmp_path / "ex1" / "alien_contact.py",
        """
        from datetime import datetime
        from enum import Enum

        from pydantic import BaseModel, Field, model_validator


        class ContactType(str, Enum):
            RADIO = "radio"
            VISUAL = "visual"
            PHYSICAL = "physical"
            TELEPATHIC = "telepathic"


            class AlienContact(BaseModel):
                contact_id: str = Field(..., min_length=5, max_length=15)
                timestamp: datetime
                location: str = Field(..., min_length=3, max_length=100)
                contact_type: ContactType
                signal_strength: float = Field(..., ge=0.0, le=10.0)
                duration_minutes: int = Field(..., ge=1, le=1440)
                witness_count: int = Field(..., ge=1, le=100)
                message_received: str | None = Field(None, max_length=500)
                is_verified: bool = False

                @model_validator(mode="after")
                def _rules(self) -> "AlienContact":
                    cid = self.contact_id
                    if not cid.startswith("AC"):
                        raise ValueError("contact id prefix")
                    if self.contact_type == ContactType.PHYSICAL and (
                        not self.is_verified
                    ):
                        raise ValueError("physical verified")
                    tele = self.contact_type == ContactType.TELEPATHIC
                    low_witness = self.witness_count < 3
                    if tele and low_witness:
                        raise ValueError("telepathic witnesses")
                    if self.signal_strength > 7.0:
                        msg = self.message_received
                        if msg is None or not str(msg).strip():
                            raise ValueError("message required")
                    return self
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_alien_contact()
    assert not tester.grouped_errors.get("Exercise 1")


def test_module09_ex2_flags_missing_crew_list_bounds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_09 import Tester

    _write(
        tmp_path / "ex2" / "space_crew.py",
        """
        from datetime import datetime
        from enum import Enum

        from pydantic import BaseModel, Field, model_validator


        class Rank(str, Enum):
            CADET = "cadet"
            OFFICER = "officer"
            LIEUTENANT = "lieutenant"
            CAPTAIN = "captain"
            COMMANDER = "commander"


        class CrewMember(BaseModel):
            member_id: str = Field(..., min_length=3, max_length=10)
            name: str = Field(..., min_length=2, max_length=50)
            rank: Rank
            age: int = Field(..., ge=18, le=80)
            specialization: str = Field(..., min_length=3, max_length=30)
            years_experience: int = Field(..., ge=0, le=50)
            is_active: bool = True


        class SpaceMission(BaseModel):
            mission_id: str = Field(..., min_length=5, max_length=15)
            mission_name: str = Field(..., min_length=3, max_length=100)
            destination: str = Field(..., min_length=3, max_length=50)
            launch_date: datetime
            duration_days: int = Field(..., ge=1, le=3650)
            crew: list[CrewMember]
            mission_status: str = "planned"
            budget_millions: float = Field(..., ge=1.0, le=10000.0)

            @model_validator(mode="after")
            def _crew_rules(self) -> "SpaceMission":
                mids = self.mission_id
                if not mids.startswith("M"):
                    raise ValueError("mid")
                ranks = {m.rank for m in self.crew}
                need = Rank.COMMANDER not in ranks and Rank.CAPTAIN not in ranks
                if need:
                    raise ValueError("need commander or captain")
                if self.duration_days > 365:
                    seasoned = sum(
                        1 for m in self.crew if m.years_experience >= 5
                    )
                    if seasoned < len(self.crew) / 2:
                        raise ValueError("experience")
                for m in self.crew:
                    if not m.is_active:
                        raise ValueError("inactive")
                return self
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_space_crew()
    errs = tester.grouped_errors.get("Exercise 2", [])
    joined = "\n".join(errs)
    assert "reject lists longer than 12" in joined


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
