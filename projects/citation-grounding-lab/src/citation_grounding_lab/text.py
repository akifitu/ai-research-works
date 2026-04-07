from __future__ import annotations

import re
from collections import Counter

TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")
NUMBER_PATTERN = re.compile(r"\b\d+(?:\.\d+)?\b")
NEGATION_TOKENS = {
    "cannot",
    "cant",
    "can't",
    "lack",
    "lacks",
    "neither",
    "never",
    "no",
    "none",
    "not",
    "without",
}
STOPWORDS = {
    "a",
    "about",
    "after",
    "all",
    "also",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "because",
    "before",
    "between",
    "both",
    "but",
    "by",
    "can",
    "does",
    "each",
    "for",
    "from",
    "had",
    "has",
    "have",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "more",
    "of",
    "on",
    "or",
    "same",
    "since",
    "so",
    "than",
    "that",
    "the",
    "their",
    "them",
    "therefore",
    "they",
    "this",
    "through",
    "to",
    "under",
    "up",
    "use",
    "uses",
    "using",
    "very",
    "was",
    "were",
    "when",
    "where",
    "which",
    "while",
    "with",
    "without",
}


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text: str) -> list[str]:
    normalized = normalize_whitespace(text)
    if not normalized:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", normalized) if part.strip()]


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def content_tokens(text: str) -> list[str]:
    return [token for token in tokenize(text) if token not in STOPWORDS and len(token) > 1]


def unique_content_tokens(text: str) -> set[str]:
    return set(content_tokens(text))


def count_content_tokens(text: str) -> Counter[str]:
    return Counter(content_tokens(text))


def numeric_tokens(text: str) -> set[str]:
    return set(NUMBER_PATTERN.findall(text))


def negation_markers(text: str) -> set[str]:
    return {token for token in tokenize(text) if token in NEGATION_TOKENS}
