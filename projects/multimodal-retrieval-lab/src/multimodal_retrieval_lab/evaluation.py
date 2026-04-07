from __future__ import annotations

from collections import defaultdict
from statistics import fmean, median

from .models import (
    RetrievalEvalConfig,
    RetrievalScenario,
    RetrievalSystem,
    SliceSummary,
    SystemEvaluation,
)


def _safe_mean(values: list[float]) -> float:
    return fmean(values) if values else 0.0


def _threshold_score(value: float, threshold: float) -> float:
    if threshold <= 0.0:
        return 1.0
    return max(0.0, min(1.0, value / threshold))


def _recall_at_k(predicted: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    hits = sum(item_id in relevant for item_id in predicted[:k])
    return hits / len(relevant)


def _reciprocal_rank(predicted: list[str], relevant: set[str]) -> float:
    for rank, item_id in enumerate(predicted, start=1):
        if item_id in relevant:
            return 1.0 / rank
    return 0.0


def _top1_accuracy(predicted: list[str], relevant: set[str]) -> float:
    return 1.0 if predicted and predicted[0] in relevant else 0.0


def _first_relevant_rank(predicted: list[str], relevant: set[str], fallback_rank: int) -> int:
    for rank, item_id in enumerate(predicted, start=1):
        if item_id in relevant:
            return rank
    return fallback_rank


def _hard_negative_hit(predicted: list[str], hard_negatives: set[str], k: int) -> float:
    return 1.0 if any(item_id in hard_negatives for item_id in predicted[:k]) else 0.0


def _slice_summary(
    slice_type: str,
    slice_value: str,
    metrics: list[dict[str, float]],
) -> SliceSummary:
    return SliceSummary(
        slice_type=slice_type,
        slice_value=slice_value,
        query_count=len(metrics),
        recall_at_k=round(_safe_mean([row["recall_at_k"] for row in metrics]), 4),
        mrr=round(_safe_mean([row["mrr"] for row in metrics]), 4),
        top1_accuracy=round(_safe_mean([row["top1_accuracy"] for row in metrics]), 4),
        hard_negative_rate=round(
            _safe_mean([row["hard_negative_hit"] for row in metrics]),
            4,
        ),
    )


def evaluate_system(
    system: RetrievalSystem,
    scenario: RetrievalScenario,
    config: RetrievalEvalConfig,
) -> SystemEvaluation:
    k = min(config.k, scenario.k)
    fallback_rank = len(scenario.assets) + 1
    gallery_ids = {asset.asset_id for asset in scenario.assets}
    recommended_ids: set[str] = set()
    query_metrics: list[dict[str, float]] = []
    slice_buckets: dict[tuple[str, str], list[dict[str, float]]] = defaultdict(list)

    for query in scenario.queries:
        predicted = query.predictions.get(system.system_id, [])[:k]
        relevant = set(query.relevant_target_ids)
        hard_negatives = set(query.hard_negative_ids)

        recall_at_k = _recall_at_k(predicted, relevant, k)
        mrr = _reciprocal_rank(predicted, relevant)
        top1_accuracy = _top1_accuracy(predicted, relevant)
        first_rank = _first_relevant_rank(predicted, relevant, fallback_rank)
        hard_negative_hit = _hard_negative_hit(predicted, hard_negatives, k)

        recommended_ids.update(item_id for item_id in predicted if item_id in gallery_ids)
        row = {
            "recall_at_k": recall_at_k,
            "mrr": mrr,
            "top1_accuracy": top1_accuracy,
            "first_rank": float(first_rank),
            "hard_negative_hit": hard_negative_hit,
        }
        query_metrics.append(row)
        slice_buckets[("direction", query.direction)].append(row)
        slice_buckets[("segment", query.segment)].append(row)

    coverage = len(recommended_ids) / len(gallery_ids) if gallery_ids else 0.0
    recall_at_k = _safe_mean([row["recall_at_k"] for row in query_metrics])
    mrr = _safe_mean([row["mrr"] for row in query_metrics])
    top1_accuracy = _safe_mean([row["top1_accuracy"] for row in query_metrics])
    median_rank = median([row["first_rank"] for row in query_metrics]) if query_metrics else 0.0
    hard_negative_rate = _safe_mean([row["hard_negative_hit"] for row in query_metrics])
    robustness_score = max(0.0, 1.0 - hard_negative_rate)

    overall_score = round(
        (0.35 * recall_at_k)
        + (0.25 * mrr)
        + (0.15 * top1_accuracy)
        + (0.10 * _threshold_score(coverage, config.coverage_floor))
        + (0.15 * robustness_score),
        4,
    )

    slice_summaries = [
        _slice_summary(slice_type, slice_value, metrics)
        for (slice_type, slice_value), metrics in sorted(slice_buckets.items())
    ]

    return SystemEvaluation(
        system=system,
        query_count=len(scenario.queries),
        recall_at_k=round(recall_at_k, 4),
        mrr=round(mrr, 4),
        top1_accuracy=round(top1_accuracy, 4),
        median_rank=round(float(median_rank), 4),
        coverage=round(coverage, 4),
        hard_negative_rate=round(hard_negative_rate, 4),
        overall_score=overall_score,
        slice_summaries=slice_summaries,
    )
