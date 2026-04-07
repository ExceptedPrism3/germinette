"""Creature classes."""

import abc


class Creature(abc.ABC):
    """Abstract creature."""

    @abc.abstractmethod
    def attack(self) -> str:
        """Abstract attack."""
        pass

    def describe(self) -> str:
        """Base description."""
        return "I am a Creature"


class Flameling(Creature):
    """Flameling."""

    def attack(self) -> str:
        return "Flameling uses Ember!"


class Pyrodon(Creature):
    """Pyrodon."""

    def attack(self) -> str:
        return "Pyrodon uses Flamethrower!"


class Aquabub(Creature):
    """Aquabub."""

    def attack(self) -> str:
        return "Aquabub uses Water Gun!"


class Torragon(Creature):
    """Torragon."""

    def attack(self) -> str:
        return "Torragon uses Hydro Pump!"
