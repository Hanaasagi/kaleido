_TAG_OPEN = "<relevant-memories>"
_TAG_CLOSE = "</relevant-memories>"


def strip_memory_tags(s: str) -> str:
    while True:
        start = s.find(_TAG_OPEN)
        if start == -1:
            break
        end = s.find(_TAG_CLOSE)
        if end == -1:
            return s[:start]
        s = s[:start] + s[end + len(_TAG_CLOSE) :]
    return s


def strip_injected_context(messages: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """messages: list of (role, content)."""
    out: list[tuple[str, str]] = []
    for role, content in messages:
        cleaned = strip_memory_tags(content).strip()
        if cleaned:
            out.append((role, cleaned))
    return out
