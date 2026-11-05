import elements
from .elements import create_air, create_earth


def healing_potion() -> str:
    earth = create_earth()
    return f"Healing potion brewed with '{earth}' and '{create_air()}'"


def strength_potion() -> str:
    fire = elements.create_fire()
    water = elements.create_water()
    return f"Strength potion brewed with '{fire}' and '{water}'"
