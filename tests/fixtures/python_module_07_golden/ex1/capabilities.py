"""Capabilities."""

import abc


class HealCapability(abc.ABC):
    """Heal mixin."""

    @abc.abstractmethod
    def heal(self) -> str:
        """Heal abstract."""
        pass


class TransformCapability(abc.ABC):
    """Transform mixin."""

    @abc.abstractmethod
    def transform(self) -> str:
        """Transform abstract."""
        pass

    @abc.abstractmethod
    def revert(self) -> str:
        """Revert abstract."""
        pass
