"""Artifact card type."""
from __future__ import annotations

from typing import Any

from ex0.Card import Card


class ArtifactCard(Card):
    """Artifact card."""

    def __init__(self, name: str, cost: int, rarity: str, bonus: str) -> None:
        super().__init__(name, cost, rarity)
        self.bonus = bonus

    def play(self) -> dict[str, Any]:
        return {"artifact_played": self.name, "mana_used": self.cost}

    def attack(self, target: str) -> dict[str, Any]:
        return {"artifact": self.name, "target": target}

    def is_playable(self) -> bool:
        return True
