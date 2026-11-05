"""Demonstrate healing and persistent transformation."""

from ex1 import HealingCreatureFactory, TransformCreatureFactory
from ex1.capabilities import HealCapability, TransformCapability


def main() -> None:
    print('Testing healing capability')
    healing = HealingCreatureFactory()
    for entity in (healing.create_base(), healing.create_evolved()):
        print(entity.describe(), entity.attack())
        if isinstance(entity, HealCapability):
            print(entity.heal())
    print('Testing transform capability')
    transform = TransformCreatureFactory()
    for entity in (transform.create_base(), transform.create_evolved()):
        print(entity.describe(), entity.attack())
        if isinstance(entity, TransformCapability):
            print(entity.transform(), entity.attack(), entity.revert())


if __name__ == '__main__':
    main()
