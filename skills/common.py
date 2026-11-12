POLITE_PREFIXES = ("please ", "can you ", "could you ", "would you ", "hey milo ", "milo ")
POLITE_SUFFIXES = (" please", " for me", " now")


def clean_text(user_input: str) -> str:
    text = user_input.lower().strip().rstrip("?!. ")
    return " ".join(text.replace(",", " ").split())


def strip_polite_prefixes(text: str) -> str:
    changed = True
    while changed:
        changed = False
        for prefix in POLITE_PREFIXES:
            if text.startswith(prefix):
                text = text.removeprefix(prefix).strip()
                changed = True
    return text


def strip_polite_suffixes(text: str) -> str:
    """'open youtube please' -> 'open youtube'."""
    for suffix in POLITE_SUFFIXES:
        if text.endswith(suffix):
            text = text.removesuffix(suffix).strip()
    return text