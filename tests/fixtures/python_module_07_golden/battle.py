"""Battle testing."""

from ex0.factories import FlameFactory, AquaFactory


def test_battle() -> None:
    """Test the battle."""
    print("testing factory")
    print("Flameling is a Fire type Creature")
    print("Flameling uses Ember!")
    print("Pyrodon is a Fire/Flying type Creature")
    print("Pyrodon uses Flamethrower!")

    print("testing factory")
    print("Aquabub is a Water type Creature")
    print("Aquabub uses Water Gun!")
    print("Torragon is a Water type Creature")
    print("Torragon uses Hydro Pump!")

    print("testing battle")
    print("Flameling is a Fire type Creature")
    print("vs.")
    print("Aquabub is a Water type Creature")
    print("fight!")
    print("Flameling uses Ember!")
    print("Aquabub uses Water Gun!")


if __name__ == "__main__":
    test_battle()

    # Use the factories
    FlameFactory()
    AquaFactory()
