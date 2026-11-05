"""Factories."""

import abc
from .transforms import Shiftling, Morphagon
from .creatures import Creature, Flameling, Pyrodon


class CreatureFactory(abc.ABC):
    """Abstract Factory."""

    @abc.abstractmethod
    def create_base(self) -> Creature:
        """Base."""
        pass

    @abc.abstractmethod
    def create_evolved(self) -> Creature:
        """Evolved."""
        pass


class FlameFactory(CreatureFactory):
    """Flame factory."""

    def create_base(self) -> Creature:
        return Flameling()

    def create_evolved(self) -> Creature:
        return Pyrodon()


class TransformCreatureFactory(CreatureFactory):
    """Transform factory."""

    def create_base(self) -> Creature:
        return Shiftling()

    def create_evolved(self) -> Creature:
        return Morphagon()
