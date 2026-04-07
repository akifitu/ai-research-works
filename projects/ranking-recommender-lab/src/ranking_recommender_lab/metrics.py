from __future__ import annotations

from statistics import fmean

from .models import AggregateMetrics, ScenarioMetrics, ScenarioResult, SystemEvaluation


def summarize_scenario(
    *,
    system_evaluations: list[SystemEvaluation],
    baseline_score: float,
    best_score: float,
    best_system_id: str,
) -> ScenarioMetrics:
    mean_ndcg_at_k = (
        fmean(evaluation.ndcg_at_k for evaluation in system_evaluations)
        if system_evaluations
        else 0.0
    )
    mean_coverage = (
        fmean(evaluation.coverage for evaluation in system_evaluations)
        if system_evaluations
        else 0.0
    )
    return ScenarioMetrics(
        system_count=len(system_evaluations),
        baseline_score=round(baseline_score, 4),
        best_score=round(best_score, 4),
        mean_ndcg_at_k=round(mean_ndcg_at_k, 4),
        mean_coverage=round(mean_coverage, 4),
        best_system_id=best_system_id,
    )


def summarize_benchmark(scenario_results: list[ScenarioResult]) -> AggregateMetrics:
    if not scenario_results:
        return AggregateMetrics(
            scenario_count=0,
            system_count=0,
            mean_ndcg_at_k=0.0,
            mean_map_at_k=0.0,
            mean_coverage=0.0,
            mean_long_tail_share=0.0,
            total_findings=0,
        )

    all_evaluations = [
        evaluation
        for scenario_result in scenario_results
        for evaluation in scenario_result.system_evaluations
    ]
    return AggregateMetrics(
        scenario_count=len(scenario_results),
        system_count=len(all_evaluations),
        mean_ndcg_at_k=round(fmean(evaluation.ndcg_at_k for evaluation in all_evaluations), 4),
        mean_map_at_k=round(fmean(evaluation.map_at_k for evaluation in all_evaluations), 4),
        mean_coverage=round(fmean(evaluation.coverage for evaluation in all_evaluations), 4),
        mean_long_tail_share=round(
            fmean(evaluation.long_tail_share for evaluation in all_evaluations),
            4,
        ),
        total_findings=sum(len(scenario.findings) for scenario in scenario_results),
    )
