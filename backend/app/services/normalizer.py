import re
from rapidfuzz import fuzz, process

_STOPWORDS = {"caso", "processo", "proc", "nº", "n°", "ref", "ação", "autos"}
_THRESHOLD = 85


def _strip_stopwords(text: str) -> str:
    tokens = [t for t in text.split() if t not in _STOPWORDS]
    return " ".join(tokens).strip()


def normalize_project_name(raw: str, existing: list[str]) -> str:
    cleaned = raw.lower().strip()
    cleaned = _strip_stopwords(cleaned)

    if not existing or not cleaned:
        return raw.title()

    result = process.extractOne(
        cleaned,
        [e.lower() for e in existing],
        scorer=fuzz.token_sort_ratio,
    )
    if result and result[1] >= _THRESHOLD:
        idx = result[2]
        return existing[idx]

    return raw.title()
