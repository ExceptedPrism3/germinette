"""Strategy pattern for turns."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class GameStrategy(ABC):
    """Abstract turn strategy."""

    @abstractmethod
    def execute_turn(self, hand: list[str]) -> dict[str, Any]:
        """Execute one turn."""


class AggressiveStrategy(GameStrategy):
    """High-damage strategy."""

    def execute_turn(self, hand: list[str]) -> dict[str, Any]:
        return {"damage_dealt": 8}
