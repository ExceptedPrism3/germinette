"""Exercise 0 entrypoint."""
from __future__ import annotations

from ex0.CreatureCard import CreatureCard


def main() -> None:
    """Run DataDeck Card Foundation demo."""
    c = CreatureCard("Fire Dragon", 5, "legendary", 7, 20)
    print("=== DataDeck Card Foundation ===")
    print("Testing Abstract Base Class Design:")
    print("CreatureCard Info:")
    print(c.name)
    print(c.rarity)
    print("Play result:")
    print(c.play())
    print("Attack result:")
    print(c.attack("Goblin Warrior"))
    print("Playable:", c.is_playable())


if __name__ == "__main__":
    main()
