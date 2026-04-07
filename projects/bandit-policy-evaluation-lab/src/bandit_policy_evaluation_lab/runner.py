from __future__ import annotations

from datetime import datetime, timezone

from .evaluation import evaluate_policy
from .metrics import summarize_benchmark, summarize_scenario
from .models import (
    BanditBenchmark,
    ExperimentResult,
    PolicyDelta,
    PolicyEvalConfig,
    ScenarioFinding,
    ScenarioResult,
)


class ExperimentRunner:
    def __init__(self, config: PolicyEvalConfig):
        self.config = config

    def run_scenario(self, scenario) -> ScenarioResult:
        policy_evaluations = [
            evaluate_policy(policy, scenario.events, self.config)
            for policy in scenario.policies
        ]
        by_policy_id = {
            evaluation.policy.policy_id: evaluation
            for evaluation in policy_evaluations
        }
        baseline_evaluation = by_policy_id[scenario.baseline_policy_id]
        best_evaluation = max(
            policy_evaluations,
            key=lambda evaluation: evaluation.overall_score,
        )

        findings: list[ScenarioFinding] = []
        deltas: list[PolicyDelta] = []
        finding_index = 1

        def add_finding(
            category: str,
            severity: str,
            related_ids: list[str],
            description: str,
        ) -> None:
            nonlocal finding_index
            findings.append(
                ScenarioFinding(
                    finding_id=f"{scenario.scenario_id}-finding-{finding_index:02d}",
                    category=category,
                    severity=severity,
                    related_ids=related_ids,
                    description=description,
                )
            )
            finding_index += 1

        for evaluation in policy_evaluations:
            if evaluation.policy.policy_id != scenario.baseline_policy_id:
                delta = round(
                    evaluation.overall_score - baseline_evaluation.overall_score,
                    4,
                )
                deltas.append(
                    PolicyDelta(
                        policy_id=evaluation.policy.policy_id,
                        delta_vs_baseline=delta,
                    )
                )
                if delta <= -self.config.regression_threshold:
                    add_finding(
                        category="BASELINE_REGRESSION",
                        severity="high",
                        related_ids=[
                            evaluation.policy.policy_id,
                            scenario.baseline_policy_id,
                        ],
                        description=(
                            f"Policy `{evaluation.policy.policy_id}` scored {abs(delta):.2f} "
                            "below the baseline."
                        ),
                    )

            if evaluation.regret_estimate >= self.config.regret_alert_threshold:
                add_finding(
                    category="REGRET_ALERT",
                    severity="high",
                    related_ids=[evaluation.policy.policy_id],
                    description=(
                        f"Policy `{evaluation.policy.policy_id}` retained "
                        f"{evaluation.regret_estimate:.2f} estimated regret."
                    ),
                )

            if evaluation.support_rate < self.config.support_floor:
                add_finding(
                    category="SUPPORT_GAP",
                    severity="medium",
                    related_ids=[evaluation.policy.policy_id],
                    description=(
                        f"Policy `{evaluation.policy.policy_id}` is only supported on "
                        f"{evaluation.support_rate:.0%} of logged events."
                    ),
                )

            if (
                evaluation.effective_sample_ratio
                < self.config.min_effective_sample_ratio
            ):
                add_finding(
                    category="VARIANCE_RISK",
                    severity="medium",
                    related_ids=[evaluation.policy.policy_id],
                    description=(
                        f"Policy `{evaluation.policy.policy_id}` has low effective sample "
                        f"ratio at {evaluation.effective_sample_ratio:.2f}."
                    ),
                )

            worst_segment = max(
                evaluation.segment_summaries,
                key=lambda summary: summary.regret_estimate,
                default=None,
            )
            if (
                worst_segment is not None
                and worst_segment.regret_estimate
                >= self.config.segment_regret_threshold
            ):
                add_finding(
                    category="SEGMENT_DROP",
                    severity="medium",
                    related_ids=[evaluation.policy.policy_id, worst_segment.segment],
                    description=(
                        f"Policy `{evaluation.policy.policy_id}` degraded on segment "
                        f"`{worst_segment.segment}` with {worst_segment.regret_estimate:.2f} regret."
                    ),
                )

        if best_evaluation.policy.policy_id != scenario.baseline_policy_id:
            add_finding(
                category="WINNER",
                severity="low",
                related_ids=[best_evaluation.policy.policy_id],
                description=(
                    f"Policy `{best_evaluation.policy.policy_id}` delivered the best "
                    f"composite score at {best_evaluation.overall_score:.2f}."
                ),
            )

        metrics = summarize_scenario(
            policy_evaluations=policy_evaluations,
            baseline_score=baseline_evaluation.overall_score,
            best_score=best_evaluation.overall_score,
            best_policy_id=best_evaluation.policy.policy_id,
        )
        return ScenarioResult(
            scenario=scenario,
            policy_evaluations=policy_evaluations,
            deltas=deltas,
            findings=findings,
            metrics=metrics,
        )

    def run_benchmark(self, benchmark: BanditBenchmark) -> ExperimentResult:
        scenario_results = [
            self.run_scenario(scenario) for scenario in benchmark.scenarios
        ]
        aggregate_metrics = summarize_benchmark(scenario_results)
        generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        return ExperimentResult(
            benchmark_id=benchmark.benchmark_id,
            benchmark_description=benchmark.description,
            config=self.config,
            scenarios=scenario_results,
            aggregate_metrics=aggregate_metrics,
            generated_at=generated_at,
        )
