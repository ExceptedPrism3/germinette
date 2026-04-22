"""Unit tests for A-Maze-ing checker SEED logic guards."""

from __future__ import annotations

from pathlib import Path

import pytest


def _write_file(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n", encoding="utf-8")


def _run_seed_logic_check(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    main_src: str,
    display_src: str,
) -> list[str]:
    from germinette.subjects.a_maze_ing import Tester

    _write_file(tmp_path / "a_maze_ing.py", main_src)
    _write_file(tmp_path / "display.py", display_src)

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_seed_interactive_regen_logic()
    return tester.grouped_errors.get("Seed Behavior", [])


def test_seed_logic_ok_with_raw_seed_forwarding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    main_src = """
from display import launch

def main():
    seed = None
    launch(seed=seed)
"""
    display_src = """
def _loop(seed=None):
    seed_provided = seed is not None
    current_seed = seed if seed is not None else 42
    act = "regen"
    if act == "regen":
        if seed_provided:
            current_seed += 1
"""
    errors = _run_seed_logic_check(
        tmp_path,
        monkeypatch,
        main_src=main_src,
        display_src=display_src,
    )
    assert not errors


def test_seed_logic_fails_with_effective_seed_forwarding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    main_src = """
from display import launch

def main():
    seed = None
    effective_seed = 42
    launch(seed=effective_seed)
"""
    display_src = """
def _loop(seed=None):
    seed_provided = seed is not None
    current_seed = seed if seed is not None else 42
    act = "regen"
    if act == "regen":
        if seed_provided:
            current_seed += 1
"""
    errors = _run_seed_logic_check(
        tmp_path,
        monkeypatch,
        main_src=main_src,
        display_src=display_src,
    )
    assert any("launch(seed=...)" in msg for msg in errors)


def test_seed_logic_fails_with_unguarded_regen_increment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    main_src = """
from display import launch

def main():
    seed = None
    launch(seed=seed)
"""
    display_src = """
def _loop(seed=None):
    current_seed = seed if seed is not None else 42
    act = "regen"
    if act == "regen":
        current_seed += 1
"""
    errors = _run_seed_logic_check(
        tmp_path,
        monkeypatch,
        main_src=main_src,
        display_src=display_src,
    )
    assert any("increments seed without a guard" in msg for msg in errors)
