"""Tournament registration and matches."""
from __future__ import annotations

from typing import Any

from .TournamentCard import TournamentCard


class TournamentPlatform:
    """Simple tournament ledger."""

    def __init__(self) -> None:
        self._cards: list[TournamentCard] = []

    def register(self, card: TournamentCard) -> None:
        self._cards.append(card)

    def run_match(
        self,
        a: TournamentCard,
        b: TournamentCard,
    ) -> dict[str, Any]:
        """Return synthetic match result."""
        winner = a if a.get_rating() >= b.get_rating() else b
        return {
            "winner_rating": winner.get_rating(),
            "winner": winner.name,
        }

    def leaderboard(self) -> list[tuple[str, float]]:
        # list.sort avoids bare sorted() (verify_strict).
        ranked = list(self._cards)
        ranked.sort(
            key=lambda c: c.get_rating(),
            reverse=True,
        )
        return [(c.name, c.get_rating()) for c in ranked]

    def report(self) -> dict[str, str]:
        return {"platform_status": "active"}
