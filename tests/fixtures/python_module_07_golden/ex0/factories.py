"""Factories."""

import abc
from .creatures import Creature, Flameling, Pyrodon, Aquabub, Torragon


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


class AquaFactory(CreatureFactory):
    """Aqua factory."""

    def create_base(self) -> Creature:
        return Aquabub()

    def create_evolved(self) -> Creature:
        return Torragon()
