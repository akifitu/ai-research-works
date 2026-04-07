from __future__ import annotations

from .models import ContextItem


def sort_context_items(items: list[ContextItem]) -> list[ContextItem]:
    indexed_items = list(enumerate(items))
    indexed_items.sort(
        key=lambda pair: (
            -pair[1].priority,
            not pair[1].relevance,
            pair[0],
        )
    )
    return [item for _, item in indexed_items]


def pack_context(items: list[ContextItem], budget_tokens: int) -> list[ContextItem]:
    if budget_tokens < 0:
        raise ValueError("budget_tokens must be non-negative")

    packed: list[ContextItem] = []
    used_tokens = 0
    for item in sort_context_items(items):
        if item.estimated_tokens <= 0:
            raise ValueError("estimated_tokens must be positive")
        if used_tokens + item.estimated_tokens > budget_tokens:
            continue
        packed.append(item)
        used_tokens += item.estimated_tokens
    return packed


def packed_tokens(items: list[ContextItem]) -> int:
    return sum(item.estimated_tokens for item in items)


def relevant_coverage(all_items: list[ContextItem], packed_items: list[ContextItem]) -> float:
    relevant_total = sum(item.estimated_tokens for item in all_items if item.relevance)
    if relevant_total == 0:
        return 1.0
    relevant_packed = sum(item.estimated_tokens for item in packed_items if item.relevance)
    return relevant_packed / relevant_total


def noise_ratio(packed_items: list[ContextItem]) -> float:
    total = packed_tokens(packed_items)
    if total == 0:
        return 0.0
    noise_tokens = sum(item.estimated_tokens for item in packed_items if not item.relevance)
    return noise_tokens / total
