"""Exercise 2 entrypoint."""
from __future__ import annotations

from .EliteCard import EliteCard


def main() -> None:
    """Run Ability System demo."""
    elite = EliteCard("Arcane Warrior", 4, "rare", 5, 10)
    print("=== DataDeck Ability System ===")
    print("EliteCard capabilities:")
    print("- Card:", elite.name)
    print("- Combatable:", elite.name)
    print("- Magical:", elite.name)
    print("Playing Arcane Warrior")
    print("Combat phase:")
    print("Attack result:", elite.combat_attack())
    print("Defense result:", elite.combat_defend())
    print("Magic phase:")
    print("Spell cast:", elite.cast_spell())
    print("Mana channel:", elite.channel_mana())


if __name__ == "__main__":
    main()
