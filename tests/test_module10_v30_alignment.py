"""Regression tests for Module 10 v3.0 checker alignment."""

from __future__ import annotations

from pathlib import Path
import textwrap

import pytest


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def test_module10_rejects_eval_exec_and_globals(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_10 import Tester

    _write(
        tmp_path / "ex0" / "lambda_spells.py",
        """
        state = 0


        def artifact_sorter(artifacts: list[dict]) -> list[dict]:
            return sorted(artifacts, key=lambda a: a["power"], reverse=True)


        def power_filter(mages: list[dict], min_power: int) -> list[dict]:
            return list(filter(lambda m: m["power"] >= min_power, mages))


        def spell_transformer(spells: list[str]) -> list[str]:
            return list(map(lambda s: f"* {s} *", spells))


        def mage_stats(mages: list[dict]) -> dict:
            eval("1+1")
            return {"max_power": 0, "min_power": 0, "avg_power": 0.0}
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_lambda_sanctum()
    errors = "\n".join(tester.grouped_errors.get("Exercise 0", []))
    assert ("Global State" in errors
            or "Forbidden Function" in errors
            or "Authorized Functions" in errors)


def test_module10_ex1_signature_contract_checked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from germinette.subjects.python_module_10 import Tester

    _write(
        tmp_path / "ex1" / "higher_magic.py",
        """
        from collections.abc import Callable


        def spell_combiner(spell1: Callable, spell2: Callable) -> Callable:
            return lambda target, power: (spell1(target, power), spell2(target, power))


        def power_amplifier(base_spell: Callable, multiplier: int) -> Callable:
            return lambda target, power: base_spell(target, power * multiplier)


        def conditional_caster(condition: Callable, spell: Callable) -> Callable:
            return lambda target, power: (
                spell(target, power)
                if condition(target, power)
                else "Spell fizzled"
            )


        def spell_sequence(spells: list[Callable]) -> Callable:
            return lambda target, power: [s(target, power) for s in spells]
        """,
    )

    monkeypatch.chdir(tmp_path)
    tester = Tester()
    tester.test_higher_realm()
    errors = "\n".join(tester.grouped_errors.get("Exercise 1", []))
    assert errors == ""
