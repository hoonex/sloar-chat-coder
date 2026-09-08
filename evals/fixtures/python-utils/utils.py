def clamp(value, low, high):
    if low > high:
        raise ValueError("low must not exceed high")
    return min(max(value, low), high)


def parse_bool(value):
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"not a boolean: {value!r}")
