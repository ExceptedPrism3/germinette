"""Creatures that heal or retain a transformed state."""

from ex0.creatures import Creature
from .capabilities import HealCapability, TransformCapability


class Sproutling(Creature, HealCapability):
    def __init__(self) -> None:
        super().__init__('Sproutling', 'Grass')

    def attack(self) -> str:
        return 'Sproutling attacks!'

    def heal(self) -> str:
        return 'Sproutling heals itself'


class Bloomelle(Sproutling):
    def __init__(self) -> None:
        Creature.__init__(self, 'Bloomelle', 'Grass/Fairy')

    def heal(self) -> str:
        return 'Bloomelle heals itself and others'


class Shiftling(Creature, TransformCapability):
    def __init__(self) -> None:
        super().__init__('Shiftling', 'Normal')
        self.transformed = False

    def attack(self) -> str:
        return 'boosted strike' if self.transformed else 'normal attack'

    def transform(self) -> str:
        self.transformed = True
        return 'transform into a sharper form'

    def revert(self) -> str:
        self.transformed = False
        return 'revert to normal'


class Morphagon(Shiftling):
    def __init__(self) -> None:
        super().__init__()
        self.name = 'Morphagon'
        self.kind = 'Normal/Dragon'
