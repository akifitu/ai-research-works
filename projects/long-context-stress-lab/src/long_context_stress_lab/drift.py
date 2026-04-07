from __future__ import annotations

import re

from .models import ContextItem

TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "because",
    "be",
    "but",
    "by",
    "for",
    "from",
    "how",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "out",
    "the",
    "their",
    "this",
    "to",
    "was",
    "what",
    "when",
    "why",
    "with",
}


def content_tokens(text: str) -> set[str]:
    return {
        token
        for token in TOKEN_PATTERN.findall(text.lower())
        if token not in STOPWORDS and len(token) > 1
    }


def token_overlap_ratio(source_text: str, target_text: str) -> float:
    source_tokens = content_tokens(source_text)
    if not source_tokens:
        return 1.0
    target_tokens = content_tokens(target_text)
    return len(source_tokens & target_tokens) / len(source_tokens)


def packed_support_ratio(answer_text: str, packed_items: list[ContextItem]) -> float:
    combined_context = " ".join(item.text for item in packed_items)
    return token_overlap_ratio(answer_text, combined_context)


def unsupported_token_rate(answer_text: str, packed_items: list[ContextItem]) -> float:
    return 1.0 - packed_support_ratio(answer_text, packed_items)


def consistency_ratio(answer_text: str, previous_answer_text: str) -> float:
    return token_overlap_ratio(answer_text, previous_answer_text)
