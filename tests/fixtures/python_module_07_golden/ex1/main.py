"""Exercise 1 entrypoint."""
from __future__ import annotations

from ex0.CreatureCard import CreatureCard

from .ArtifactCard import ArtifactCard
from .Deck import Deck
from .SpellCard import SpellCard


def main() -> None:
    """Run Deck Builder demo."""
    deck = Deck()
    deck.add(CreatureCard("Goblin", 1, "common", 2, 1))
    deck.add(SpellCard("Zap", 2, "common", "damage"))
    deck.add(ArtifactCard("Ring", 3, "rare", "draw"))
    print("=== DataDeck Deck Builder ===")
    print("Building deck with different card types...")
    print("Deck stats:")
    for key, val in deck.stats().items():
        print(f"'{key}': {val}")
    print("Drew:")
    top = deck.draw()
    print(top.name if top else "")
    print("Play result:")
    print(top.play() if top else {})
    print("Same interface, different card behaviors")


if __name__ == "__main__":
    main()
