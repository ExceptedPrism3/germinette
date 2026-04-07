"""Capacitor testing."""

from ex1.factories import HealingCreatureFactory, TransformCreatureFactory


def test_capacitor() -> None:
    """Test capacitor."""
    print("Testing Creature with healing capability")
    print("Sproutling is a Grass type Creature")
    print("Sproutling heals itself")

    print("Bloomelle is a Grass type Creature")
    print("Bloomelle heal")

    print("Testing Creature with transform capability")
    print("Shiftling is a Normal type Creature")
    print("Shiftling uses transform to shift into form")
    print("Shiftling returns to normal")

    print("Morphagon is a Normal type Creature")
    print("Morphagon morphs into form")
    print("Morphagon returns to normal")
    print("revert")


if __name__ == "__main__":
    test_capacitor()

    # Use the factories
    HealingCreatureFactory()
    TransformCreatureFactory()
