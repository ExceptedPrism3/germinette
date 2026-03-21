"""Tournament-eligible card."""
from __future__ import annotations

from typing import Any

from ex0.Card import Card
from ex2.Combatable import Combatable

from .Rankable import Rankable


class TournamentCard(Card, Combatable, Rankable):
    """Card that can fight and be ranked."""

    def __init__(
        self,
        name: str,
        cost: int,
        rarity: str,
        attack: int,
        health: int,
        rating: float,
    ) -> None:
        super().__init__(name, cost, rarity)
        self._attack = attack
        self._health = health
        self._rating = rating

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
        return {"damage": 3}

    def combat_defend(self) -> dict[str, Any]:
        return {"still_alive": True}

    def get_rating(self) -> float:
        return self._rating
