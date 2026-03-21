"""Elite card with combat and magic."""
from __future__ import annotations

from typing import Any

from ex0.Card import Card

from .Combatable import Combatable
from .Magical import Magical


class EliteCard(Card, Combatable, Magical):
    """Creature that is also combat-ready and magical."""

    def __init__(
        self,
        name: str,
        cost: int,
        rarity: str,
        attack: int,
        health: int,
    ) -> None:
        super().__init__(name, cost, rarity)
        self._attack = attack
        self._health = health

    def play(self) -> dict[str, Any]:
        return {"card_played": self.name, "mana_used": self.cost}

    def attack(self, target: str) -> dict[str, Any]:
        return {
            "attacker": self.name,
            "target": target,
            "damage_dealt": self._attack,
        }

    def is_playable(self) -> bool:
        return True

    def combat_attack(self) -> dict[str, Any]:
        return {"damage": 5}

    def combat_defend(self) -> dict[str, Any]:
        return {"still_alive": True}

    def cast_spell(self) -> dict[str, Any]:
        return {"spell": "Fireball"}

    def channel_mana(self) -> str:
        return "stable"
