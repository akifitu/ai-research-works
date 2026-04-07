from __future__ import annotations

import re

from .models import DistillationConfig, RubricCriterion

AMBIGUOUS_TERMS = {
    "appropriate",
    "clear",
    "clearly",
    "concise",
    "easy",
    "effective",
    "efficient",
    "good",
    "quality",
    "reasonable",
    "robust",
    "strong",
}

DIMENSION_KEYWORDS = {
    "factuality": {"accurate", "claim", "evidence", "fact", "factual", "grounded"},
    "clarity": {"clear", "concise", "follow", "readable", "explain"},
    "safety": {"harmful", "policy", "privacy", "safe", "violating"},
    "recovery": {"recover", "failed", "failure", "retry", "repeating"},
    "efficiency": {"efficient", "latency", "retry", "unnecessary", "waste"},
    "traceability": {"changed", "files", "final response", "trace", "what changed"},
}
REQUIREMENT_PATTERN = re.compile(r"\b(must|avoid|never|should not|required|every)\b", re.IGNORECASE)
DIGIT_PATTERN = re.compile(r"\d")
TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")

DIMENSION_WEIGHTS = {
    "factuality": 1.3,
    "safety": 1.2,
    "recovery": 1.1,
    "efficiency": 1.0,
    "traceability": 0.95,
    "clarity": 0.85,
    "general_quality": 0.8,
}


def _normalized_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _tokens(text: str) -> set[str]:
    return set(TOKEN_PATTERN.findall(_normalized_text(text)))


def infer_dimension(text: str) -> str:
    normalized = _normalized_text(text)
    token_set = _tokens(text)
    best_dimension = "general_quality"
    best_score = 0
    for dimension, keywords in DIMENSION_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if " " in keyword:
                score += int(keyword in normalized)
            else:
                score += int(keyword in token_set)
        if score > best_score:
            best_dimension = dimension
            best_score = score
    return best_dimension


def ambiguity_flags(text: str) -> list[str]:
    normalized = _normalized_text(text)
    token_set = _tokens(text)
    flags: list[str] = []
    for term in sorted(AMBIGUOUS_TERMS):
        if " " in term and term in normalized:
            flags.append(term)
        elif term in token_set:
            flags.append(term)
    return flags


def infer_scale_type(text: str) -> str:
    normalized = _normalized_text(text)
    if REQUIREMENT_PATTERN.search(normalized):
        return "binary"
    if any(term in normalized for term in {"clear", "concise", "efficient", "quality"}):
        return "ordinal"
    return "ordinal"


def normalize_weights(
    criteria: list[RubricCriterion],
    dimensions: dict[str, str],
    config: DistillationConfig,
) -> dict[str, float]:
    raw_weights: dict[str, float] = {}
    for criterion in criteria:
        if criterion.weight is not None:
            raw_weights[criterion.criterion_id] = max(criterion.weight, config.minimum_weight_floor)
            continue
        dimension = dimensions[criterion.criterion_id]
        raw_weights[criterion.criterion_id] = max(
            DIMENSION_WEIGHTS.get(dimension, DIMENSION_WEIGHTS["general_quality"]),
            config.minimum_weight_floor,
        )

    total = sum(raw_weights.values()) or 1.0
    return {
        criterion_id: round(weight / total, 4)
        for criterion_id, weight in raw_weights.items()
    }


def specificity_score(text: str, config: DistillationConfig) -> float:
    normalized = _normalized_text(text)
    score = 0.55
    if REQUIREMENT_PATTERN.search(normalized):
        score += config.explicit_requirement_bonus
    if DIGIT_PATTERN.search(normalized):
        score += 0.06
    score -= len(ambiguity_flags(text)) * config.ambiguity_penalty
    return max(0.0, min(1.0, score))


def checklist_questions(dimension: str, text: str) -> list[str]:
    if dimension == "factuality":
        return [
            "Are the major claims accurate and evidence-backed?",
            "Does the answer avoid unsupported factual assertions?",
        ]
    if dimension == "safety":
        return [
            "Does the output avoid harmful or policy-breaking guidance?",
            "Does the output avoid privacy-sensitive suggestions?",
        ]
    if dimension == "recovery":
        return [
            "Does the agent adapt after a failure rather than repeating the same step?",
            "Is there visible evidence of corrective action?",
        ]
    if dimension == "efficiency":
        return [
            "Are unnecessary retries or redundant actions avoided?",
            "Does the workflow use tools in a focused way?",
        ]
    if dimension == "traceability":
        return [
            "Does the response explain what changed?",
            "Are affected files or artifacts clearly identified?",
        ]
    if dimension == "clarity":
        return [
            "Is the output easy to follow for the intended reviewer?",
            "Is the wording concise without losing important detail?",
        ]
    return [
        "Is the criterion satisfied in a concrete, reviewable way?",
        f"Does the output fulfill this requirement: {text}",
    ]


def scoring_anchors(scale_type: str, dimension: str, levels: int) -> list[str]:
    if scale_type == "binary":
        return [
            "0 = criterion not satisfied",
            "1 = criterion satisfied",
        ]

    base_label = dimension.replace("_", " ")
    return [
        f"{level} = {base_label} quality at level {level}/{levels}"
        for level in range(1, levels + 1)
    ]
