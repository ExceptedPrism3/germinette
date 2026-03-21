"""Exercise 4 entrypoint."""
from __future__ import annotations

from .TournamentCard import TournamentCard
from .TournamentPlatform import TournamentPlatform


def main() -> None:
    """Run Tournament Platform demo."""
    dragon = TournamentCard("Fire Dragon", 5, "legendary", 7, 20, 99.5)
    goblin = TournamentCard("Goblin Scout", 1, "common", 1, 1, 12.0)
    platform = TournamentPlatform()
    platform.register(dragon)
    platform.register(goblin)
    print("=== DataDeck Tournament Platform ===")
    print("Registering Tournament Cards...")
    print("Fire Dragon (ID: dragon_001):")
    print("- Interfaces: [Card, Combatable, Rankable]")
    print("- Rating:", dragon.get_rating())
    print("Creating tournament match...")
    match = platform.run_match(dragon, goblin)
    print("Match result:")
    print(match)
    print("winner_rating")
    print("Tournament Leaderboard:")
    for i, (name, _rating) in enumerate(platform.leaderboard(), start=1):
        print(f"{i}. {name}")
    print("Platform Report:")
    print(platform.report())


if __name__ == "__main__":
    main()
