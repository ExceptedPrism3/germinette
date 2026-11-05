"""Capabilities."""

import abc


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
