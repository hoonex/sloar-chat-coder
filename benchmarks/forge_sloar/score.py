def normalize_score(value: int) -> int:
    """Clamp an integer score to the inclusive range 0..100."""
    if value < 0:
        return 0
    if value > 100:
        return 100
    return value
