from .light_spellbook import light_spell_allowed_ingredients


def validate_ingredients(ingredients: str) -> str:
    allowed = light_spell_allowed_ingredients()
    valid = any(item in ingredients.lower() for item in allowed)
    status = "VALID" if valid else "INVALID"
    return f"{ingredients} - {status}"
