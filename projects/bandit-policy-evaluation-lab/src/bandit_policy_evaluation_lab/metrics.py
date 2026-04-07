from __future__ import annotations

from statistics import fmean

from .models import AggregateMetrics, PolicyEvaluation, ScenarioMetrics, ScenarioResult


def summarize_scenario(
    *,
    policy_evaluations: list[PolicyEvaluation],
    baseline_score: float,
    best_score: float,
    best_policy_id: str,
) -> ScenarioMetrics:
    mean_score = (
        fmean(evaluation.overall_score for evaluation in policy_evaluations)
        if policy_evaluations
        else 0.0
    )
    mean_support_rate = (
        fmean(evaluation.support_rate for evaluation in policy_evaluations)
        if policy_evaluations
        else 0.0
    )
    return ScenarioMetrics(
        policy_count=len(policy_evaluations),
        baseline_score=round(baseline_score, 4),
        best_score=round(best_score, 4),
        mean_score=round(mean_score, 4),
        mean_support_rate=round(mean_support_rate, 4),
        best_policy_id=best_policy_id,
    )


def summarize_benchmark(scenario_results: list[ScenarioResult]) -> AggregateMetrics:
    if not scenario_results:
        return AggregateMetrics(
            scenario_count=0,
            policy_count=0,
            mean_snips_reward=0.0,
            mean_support_rate=0.0,
            mean_effective_sample_ratio=0.0,
            mean_regret_estimate=0.0,
            total_findings=0,
        )

    all_evaluations = [
        evaluation
        for scenario_result in scenario_results
        for evaluation in scenario_result.policy_evaluations
    ]
    return AggregateMetrics(
        scenario_count=len(scenario_results),
        policy_count=len(all_evaluations),
        mean_snips_reward=round(
            fmean(evaluation.snips_reward for evaluation in all_evaluations),
            4,
        ),
        mean_support_rate=round(
            fmean(evaluation.support_rate for evaluation in all_evaluations),
            4,
        ),
        mean_effective_sample_ratio=round(
            fmean(evaluation.effective_sample_ratio for evaluation in all_evaluations),
            4,
        ),
        mean_regret_estimate=round(
            fmean(evaluation.regret_estimate for evaluation in all_evaluations),
            4,
        ),
        total_findings=sum(len(scenario.findings) for scenario in scenario_results),
    )
