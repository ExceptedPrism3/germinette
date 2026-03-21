"""Combat interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Combatable(ABC):
    """Cards that can enter combat."""

    @abstractmethod
    def combat_attack(self) -> dict[str, Any]:
        """Perform combat attack."""

    @abstractmethod
    def combat_defend(self) -> dict[str, Any]:
        """Defend in combat."""
