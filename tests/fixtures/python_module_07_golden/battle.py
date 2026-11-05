"""Demonstrate both factories and battle their base creatures."""

from ex0 import AquaFactory, CreatureFactory, FlameFactory


def test_factory(factory: CreatureFactory) -> None:
    print('Testing factory')
    for entity in (factory.create_base(), factory.create_evolved()):
        print(entity.describe())
        print(entity.attack())


def battle(first: CreatureFactory, second: CreatureFactory) -> None:
    print('Testing battle')
    left, right = first.create_base(), second.create_base()
    print(left.describe(), 'vs.', right.describe())
    print(left.attack(), right.attack())


if __name__ == '__main__':
    flame, aqua = FlameFactory(), AquaFactory()
    test_factory(flame)
    test_factory(aqua)
    battle(flame, aqua)
