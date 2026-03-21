"""Ranking interface."""
from __future__ import annotations

from abc import ABC, abstractmethod


class Rankable(ABC):
    """Objects with a competitive rating."""

    @abstractmethod
    def get_rating(self) -> float:
        """Return current rating."""
