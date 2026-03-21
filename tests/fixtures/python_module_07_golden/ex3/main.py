"""Exercise 3 entrypoint."""
from __future__ import annotations

from .CardFactory import FantasyCardFactory
from .GameStrategy import AggressiveStrategy


def main() -> None:
    """Run Game Engine demo."""
    factory = FantasyCardFactory()
    strategy = AggressiveStrategy()
    print("=== DataDeck Game Engine ===")
    print("Configuring Fantasy Card Game...")
    print("Factory:", factory.__class__.__name__)
    print("Strategy:", strategy.__class__.__name__)
    print("Available types:")
    print("- creature")
    print("Simulating aggressive turn...")
    print("Hand:", ["Strike", "Fireball"])
    print("Turn execution:")
    print("Actions:")
    print(strategy.execute_turn(["Strike", "Fireball"]))
    print("Game Report:")
    print("Abstract Factory + Strategy Pattern: Maximum flexibility achieved!")


if __name__ == "__main__":
    main()
