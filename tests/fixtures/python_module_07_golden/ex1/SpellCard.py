"""Spell card type."""
from __future__ import annotations

from typing import Any

from ex0.Card import Card


class SpellCard(Card):
    """Spell card."""

    def __init__(self, name: str, cost: int, rarity: str, effect: str) -> None:
        super().__init__(name, cost, rarity)
        self.effect = effect

    def play(self) -> dict[str, Any]:
        return {"spell_played": self.name, "mana_used": self.cost}

    def attack(self, target: str) -> dict[str, Any]:
        return {"spell": self.name, "target": target}

    def is_playable(self) -> bool:
        return True
