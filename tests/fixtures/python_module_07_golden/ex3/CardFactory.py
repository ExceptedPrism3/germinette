"""Abstract factory for cards."""
from __future__ import annotations

from abc import ABC, abstractmethod


class CardFactory(ABC):
    """Creates themed cards."""

    @abstractmethod
    def create_creature(self) -> str:
        """Create a creature name."""


class FantasyCardFactory(CardFactory):
    """Fantasy-themed factory."""

    def create_creature(self) -> str:
        return "goblin"
