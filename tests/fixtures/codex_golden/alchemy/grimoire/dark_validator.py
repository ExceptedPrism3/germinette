from .dark_spellbook import dark_spell_allowed_ingredients


def dark_validate_ingredients(ingredients: str) -> str:
    allowed = dark_spell_allowed_ingredients()
    valid = any(item in ingredients.lower() for item in allowed)
    return f"{ingredients} - {'VALID' if valid else 'INVALID'}"
