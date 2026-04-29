"""Regression tests for module auto-detection signatures."""

from __future__ import annotations

from pathlib import Path

import pytest


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")


def test_detector_does_not_misclassify_module09_as_module07(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.core import ModuleDetector

    _touch(tmp_path / "ex0" / "__init__.py")
    _touch(tmp_path / "ex1" / "__init__.py")
    _touch(tmp_path / "ex2" / "__init__.py")
    _touch(tmp_path / "ex0" / "space_station.py")
    _touch(tmp_path / "ex1" / "alien_contact.py")
    _touch(tmp_path / "ex2" / "space_crew.py")

    monkeypatch.chdir(tmp_path)
    detected = ModuleDetector.detect()
    assert detected == "python_module_09"


def test_detector_prefers_stronger_module09_file_signature(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.core import ModuleDetector

    # Generic shared structure (can appear in multiple modules)
    _touch(tmp_path / "ex0" / "__init__.py")
    _touch(tmp_path / "ex1" / "__init__.py")
    _touch(tmp_path / "ex2" / "__init__.py")

    # One DataDeck marker plus full Cosmic Data marker set.
    _touch(tmp_path / "battle.py")
    _touch(tmp_path / "ex0" / "space_station.py")
    _touch(tmp_path / "ex1" / "alien_contact.py")
    _touch(tmp_path / "ex2" / "space_crew.py")

    monkeypatch.chdir(tmp_path)
    assert ModuleDetector.detect() == "python_module_09"
