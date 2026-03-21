"""Concrete creature card."""
from __future__ import annotations

from typing import Any

from ex0.Card import Card


class CreatureCard(Card):
    """Creature implementation."""

    def __init__(
        self,
        name: str,
        cost: int,
        rarity: str,
        attack: int,
        health: int,
    ) -> None:
        super().__init__(name, cost, rarity)
        self.attack_power = attack
        self.health = health

    def play(self) -> dict[str, Any]:
        return {"card_played": self.name, "mana_used": self.cost}

    def attack(self, target: str) -> dict[str, Any]:
        return {
            "attacker": self.name,
            "target": target,
            "damage_dealt": self.attack_power,
        }

    def is_playable(self) -> bool:
        return False
