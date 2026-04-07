"""Strategies."""

import abc


class BattleStrategy(abc.ABC):
    """Strategy abstract."""

    @abc.abstractmethod
    def act(self) -> None:
        """Act."""
        pass

    @abc.abstractmethod
    def is_valid(self) -> bool:
        """Validate."""
        pass


class NormalStrategy(BattleStrategy):
    """Normal Strategy."""

    def act(self) -> None:
        pass

    def is_valid(self) -> bool:
        return True


class AggressiveStrategy(BattleStrategy):
    """Aggresive Strategy."""

    def act(self) -> None:
        pass

    def is_valid(self) -> bool:
        return True


class DefensiveStrategy(BattleStrategy):
    """Defensive Strategy."""

    def act(self) -> None:
        pass

    def is_valid(self) -> bool:
        return True
