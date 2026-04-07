from __future__ import annotations

import re


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]+")


def normalize_text(value: str) -> list[str]:
    return TOKEN_PATTERN.findall(value.lower())


def safe_divide(numerator: float, denominator: float) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


def token_overlap(reference: str, prediction: str) -> float:
    reference_tokens = set(normalize_text(reference))
    prediction_tokens = set(normalize_text(prediction))
    return safe_divide(len(reference_tokens & prediction_tokens), len(reference_tokens | prediction_tokens))


def lcs_length(left: list[str], right: list[str]) -> int:
    previous = [0] * (len(right) + 1)
    for left_token in left:
        current = [0]
        for column, right_token in enumerate(right, start=1):
            if left_token == right_token:
                current.append(previous[column - 1] + 1)
            else:
                current.append(max(previous[column], current[-1]))
        previous = current
    return previous[-1]


def lcs_similarity(reference: str, prediction: str) -> float:
    reference_tokens = normalize_text(reference)
    prediction_tokens = normalize_text(prediction)
    return safe_divide(lcs_length(reference_tokens, prediction_tokens), len(reference_tokens))


def _entity_key(value: str) -> str:
    return " ".join(normalize_text(value))


def entity_f1(expected: list[str], predicted: list[str]) -> tuple[float, float, float]:
    expected_set = {_entity_key(entity) for entity in expected if _entity_key(entity)}
    predicted_set = {_entity_key(entity) for entity in predicted if _entity_key(entity)}
    true_positive = len(expected_set & predicted_set)
    precision = safe_divide(true_positive, len(predicted_set))
    recall = safe_divide(true_positive, len(expected_set))
    f1 = safe_divide(2 * precision * recall, precision + recall)
    return precision, recall, f1
