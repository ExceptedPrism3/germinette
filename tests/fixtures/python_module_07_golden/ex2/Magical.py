"""Magic interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Magical(ABC):
    """Cards that cast spells."""

    @abstractmethod
    def cast_spell(self) -> dict[str, Any]:
        """Cast a spell."""

    @abstractmethod
    def channel_mana(self) -> str:
        """Describe mana channel."""
