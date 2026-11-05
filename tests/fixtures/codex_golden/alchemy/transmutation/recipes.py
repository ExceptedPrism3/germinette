import elements
from ..elements import create_air
from ..potions import strength_potion


def lead_to_gold() -> str:
    return (f"Recipe transmuting Lead to Gold: brew '{create_air()}' and "
            f"'{strength_potion()}' mixed with '{elements.create_fire()}'")
