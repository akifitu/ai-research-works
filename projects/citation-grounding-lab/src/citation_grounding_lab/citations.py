from __future__ import annotations

import re

from .text import normalize_whitespace

CITATION_PATTERN = re.compile(r"\[([A-Za-z0-9._:-]+)\]")


def extract_citation_ids(text: str) -> list[str]:
    seen: set[str] = set()
    ordered_ids: list[str] = []
    for match in CITATION_PATTERN.findall(text):
        if match not in seen:
            seen.add(match)
            ordered_ids.append(match)
    return ordered_ids


def strip_inline_citations(text: str) -> str:
    return normalize_whitespace(CITATION_PATTERN.sub("", text))
