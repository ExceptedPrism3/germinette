"""Deck of cards."""
from __future__ import annotations

from typing import Optional

from ex0.Card import Card
from ex0.CreatureCard import CreatureCard

from .ArtifactCard import ArtifactCard
from .SpellCard import SpellCard


class Deck:
    """Simple deck with one of each card type."""

    def __init__(self) -> None:
        self._cards: list[Card] = []

    def add(self, card: Card) -> None:
        self._cards.append(card)

    def stats(self) -> dict[str, int]:
        creatures = sum(1 for c in self._cards if isinstance(c, CreatureCard))
        spells = sum(1 for c in self._cards if isinstance(c, SpellCard))
        artifacts = sum(1 for c in self._cards if isinstance(c, ArtifactCard))
        return {
            "total_cards": len(self._cards),
            "creatures": creatures,
            "spells": spells,
            "artifacts": artifacts,
        }

    def draw(self) -> Optional[Card]:
        return self._cards[0] if self._cards else None
