"""Two creature families with descriptions supplied by their shared base."""

from abc import ABC, abstractmethod


class Creature(ABC):
    def __init__(self, name: str = 'Creature', kind: str = 'Normal') -> None:
        self.name = name
        self.kind = kind

    @abstractmethod
    def attack(self) -> str:
        pass

    def describe(self) -> str:
        return f'{self.name} is a {self.kind} type Creature'


class Flameling(Creature):
    def __init__(self) -> None:
        super().__init__('Flameling', 'Fire')

    def attack(self) -> str:
        return 'Flameling uses Ember!'


class Pyrodon(Creature):
    def __init__(self) -> None:
        super().__init__('Pyrodon', 'Fire/Flying')

    def attack(self) -> str:
        return 'Pyrodon uses Flamethrower!'


class Aquabub(Creature):
    def __init__(self) -> None:
        super().__init__('Aquabub', 'Water')

    def attack(self) -> str:
        return 'Aquabub uses Water Gun!'


class Torragon(Creature):
    def __init__(self) -> None:
        super().__init__('Torragon', 'Water')

    def attack(self) -> str:
        return 'Torragon uses Hydro Pump!'
