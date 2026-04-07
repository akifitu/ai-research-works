from __future__ import annotations

import math
from collections import defaultdict
from statistics import fmean

from .models import (
    RankingEvalConfig,
    RankingScenario,
    RankingSystem,
    SegmentSummary,
    SystemEvaluation,
)


def _safe_mean(values: list[float]) -> float:
    return fmean(values) if values else 0.0


def _threshold_score(value: float, threshold: float) -> float:
    if threshold <= 0.0:
        return 1.0
    return max(0.0, min(1.0, value / threshold))


def _precision_at_k(predicted: list[str], relevant: set[str], k: int) -> float:
    hits = sum(item in relevant for item in predicted[:k])
    return hits / k if k > 0 else 0.0


def _recall_at_k(predicted: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    hits = sum(item in relevant for item in predicted[:k])
    return hits / len(relevant)


def _average_precision_at_k(predicted: list[str], relevant: set[str], k: int) -> float:
    if not relevant or k <= 0:
        return 0.0
    hit_count = 0
    precision_sum = 0.0
    for rank, item_id in enumerate(predicted[:k], start=1):
        if item_id in relevant:
            hit_count += 1
            precision_sum += hit_count / rank
    return precision_sum / min(len(relevant), k)


def _dcg_at_k(predicted: list[str], relevance_map: dict[str, int], k: int) -> float:
    total = 0.0
    for rank, item_id in enumerate(predicted[:k], start=1):
        grade = relevance_map.get(item_id, 0)
        if grade <= 0:
            continue
        total += (2**grade - 1) / math.log2(rank + 1)
    return total


def _ndcg_at_k(predicted: list[str], relevance_map: dict[str, int], k: int) -> float:
    ideal_grades = sorted(relevance_map.values(), reverse=True)
    idcg = sum(
        (2**grade - 1) / math.log2(rank + 1)
        for rank, grade in enumerate(ideal_grades[:k], start=1)
    )
    if idcg <= 0.0:
        return 0.0
    return _dcg_at_k(predicted, relevance_map, k) / idcg


def _segment_summary(segment: str, metrics: list[dict[str, float]]) -> SegmentSummary:
    return SegmentSummary(
        segment=segment,
        query_count=len(metrics),
        ndcg_at_k=round(_safe_mean([row["ndcg_at_k"] for row in metrics]), 4),
        map_at_k=round(_safe_mean([row["map_at_k"] for row in metrics]), 4),
        hit_rate=round(_safe_mean([row["hit"] for row in metrics]), 4),
        long_tail_share=round(_safe_mean([row["long_tail_share"] for row in metrics]), 4),
    )


def evaluate_system(
    system: RankingSystem,
    scenario: RankingScenario,
    config: RankingEvalConfig,
) -> SystemEvaluation:
    k = min(config.k, scenario.k)
    long_tail_index = {item.item_id: item.is_long_tail for item in scenario.catalog}
    recommended_items: set[str] = set()
    query_metrics: list[dict[str, float]] = []
    segment_buckets: dict[str, list[dict[str, float]]] = defaultdict(list)

    for query in scenario.queries:
        predicted = query.predictions.get(system.system_id, [])[:k]
        relevant_map = {judgment.item_id: judgment.grade for judgment in query.relevant_items}
        relevant = set(relevant_map)

        precision_at_k = _precision_at_k(predicted, relevant, k)
        recall_at_k = _recall_at_k(predicted, relevant, k)
        map_at_k = _average_precision_at_k(predicted, relevant, k)
        ndcg_at_k = _ndcg_at_k(predicted, relevant_map, k)
        hit = 1.0 if any(item_id in relevant for item_id in predicted) else 0.0
        long_tail_share = (
            sum(long_tail_index.get(item_id, False) for item_id in predicted) / k
            if k > 0
            else 0.0
        )

        recommended_items.update(predicted)
        row = {
            "precision_at_k": precision_at_k,
            "recall_at_k": recall_at_k,
            "map_at_k": map_at_k,
            "ndcg_at_k": ndcg_at_k,
            "hit": hit,
            "long_tail_share": long_tail_share,
        }
        query_metrics.append(row)
        segment_buckets[query.segment].append(row)

    coverage = (
        len(recommended_items) / len(scenario.catalog)
        if scenario.catalog
        else 0.0
    )
    precision_at_k = _safe_mean([row["precision_at_k"] for row in query_metrics])
    recall_at_k = _safe_mean([row["recall_at_k"] for row in query_metrics])
    map_at_k = _safe_mean([row["map_at_k"] for row in query_metrics])
    ndcg_at_k = _safe_mean([row["ndcg_at_k"] for row in query_metrics])
    hit_rate = _safe_mean([row["hit"] for row in query_metrics])
    long_tail_share = _safe_mean([row["long_tail_share"] for row in query_metrics])

    overall_score = round(
        (0.30 * ndcg_at_k)
        + (0.25 * map_at_k)
        + (0.15 * precision_at_k)
        + (0.10 * recall_at_k)
        + (0.10 * hit_rate)
        + (0.05 * _threshold_score(coverage, config.coverage_floor))
        + (0.05 * _threshold_score(long_tail_share, config.long_tail_floor)),
        4,
    )

    segment_summaries = [
        _segment_summary(segment, metrics)
        for segment, metrics in sorted(segment_buckets.items())
    ]

    return SystemEvaluation(
        system=system,
        query_count=len(scenario.queries),
        ndcg_at_k=round(ndcg_at_k, 4),
        map_at_k=round(map_at_k, 4),
        precision_at_k=round(precision_at_k, 4),
        recall_at_k=round(recall_at_k, 4),
        hit_rate=round(hit_rate, 4),
        coverage=round(coverage, 4),
        long_tail_share=round(long_tail_share, 4),
        overall_score=overall_score,
        segment_summaries=segment_summaries,
    )
