def light_spell_allowed_ingredients() -> list[str]:
    return ["earth", "air", "fire", "water"]


def light_spell_record(spell_name: str, ingredients: str) -> str:
    from .light_validator import validate_ingredients
    result = validate_ingredients(ingredients)
    status = "rejected" if "INVALID" in result else "recorded"
    return f"Spell {status}: {spell_name} ({result})"
