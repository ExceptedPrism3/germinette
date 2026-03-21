"""Abstract base card."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Card(ABC):
    """Abstract playing card."""

    def __init__(self, name: str, cost: int, rarity: str) -> None:
        self.name = name
        self.cost = cost
        self.rarity = rarity

    @abstractmethod
    def play(self) -> dict[str, Any]:
        """Play this card."""

    @abstractmethod
    def attack(self, target: str) -> dict[str, Any]:
        """Attack a target."""

    @abstractmethod
    def is_playable(self) -> bool:
        """Whether the card can be played."""
