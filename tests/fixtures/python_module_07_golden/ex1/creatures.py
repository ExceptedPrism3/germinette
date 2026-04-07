"""Ex1 Creatures."""

from ex0.creatures import Creature
from .capabilities import HealCapability, TransformCapability


class Sproutling(Creature, HealCapability):
    """Sproutling."""

    def attack(self) -> str:
        return "Sproutling attacks!"

    def heal(self) -> str:
        return "Sproutling heals itself"


class Bloomelle(Creature, HealCapability):
    """Bloomelle."""

    def attack(self) -> str:
        return "Bloomelle attacks!"

    def heal(self) -> str:
        return "Bloomelle heals"


class Shiftling(Creature, TransformCapability):
    """Shiftling."""

    def attack(self) -> str:
        return "Shiftling attacks!"

    def transform(self) -> str:
        return "Shiftling shifts into form"

    def revert(self) -> str:
        return "Shiftling returns to normal"


class Morphagon(Creature, TransformCapability):
    """Morphagon."""

    def attack(self) -> str:
        return "Morphagon attacks!"

    def transform(self) -> str:
        return "Morphagon morphs into form"

    def revert(self) -> str:
        return "Morphagon returns to normal"
