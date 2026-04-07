from __future__ import annotations

from statistics import fmean

from .models import AggregateMetrics, TaskMetrics, TaskResult, VariantScore


def summarize_task(
    *,
    scored_variants: list[VariantScore],
    baseline_score: float,
    best_score: float,
    best_variant_id: str,
) -> TaskMetrics:
    completion_rate = (
        sum(score.variant.completed for score in scored_variants) / len(scored_variants)
        if scored_variants
        else 0.0
    )
    mean_score = (
        fmean(score.overall_score for score in scored_variants) if scored_variants else 0.0
    )
    return TaskMetrics(
        variant_count=len(scored_variants),
        completion_rate=round(completion_rate, 4),
        baseline_score=round(baseline_score, 4),
        best_score=round(best_score, 4),
        mean_score=round(mean_score, 4),
        best_variant_id=best_variant_id,
    )


def summarize_benchmark(task_results: list[TaskResult]) -> AggregateMetrics:
    if not task_results:
        return AggregateMetrics(
            task_count=0,
            variant_count=0,
            mean_completion_rate=0.0,
            mean_score=0.0,
            mean_recovery_score=0.0,
            mean_latency_score=0.0,
            total_findings=0,
        )

    all_scores = [
        score
        for task_result in task_results
        for score in task_result.scored_variants
    ]
    return AggregateMetrics(
        task_count=len(task_results),
        variant_count=len(all_scores),
        mean_completion_rate=round(
            fmean(task.metrics.completion_rate for task in task_results), 4
        ),
        mean_score=round(fmean(score.overall_score for score in all_scores), 4),
        mean_recovery_score=round(fmean(score.recovery_score for score in all_scores), 4),
        mean_latency_score=round(fmean(score.latency_score for score in all_scores), 4),
        total_findings=sum(len(task.findings) for task in task_results),
    )

