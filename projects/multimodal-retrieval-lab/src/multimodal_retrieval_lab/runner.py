from __future__ import annotations

from datetime import datetime, timezone

from .evaluation import evaluate_system
from .metrics import summarize_benchmark, summarize_scenario
from .models import (
    ExperimentResult,
    RetrievalBenchmark,
    RetrievalEvalConfig,
    ScenarioFinding,
    ScenarioResult,
    SystemDelta,
)


class ExperimentRunner:
    def __init__(self, config: RetrievalEvalConfig):
        self.config = config

    def run_scenario(self, scenario) -> ScenarioResult:
        system_evaluations = [
            evaluate_system(system, scenario, self.config)
            for system in scenario.systems
        ]
        by_system_id = {
            evaluation.system.system_id: evaluation
            for evaluation in system_evaluations
        }
        baseline_evaluation = by_system_id[scenario.baseline_system_id]
        best_evaluation = max(
            system_evaluations,
            key=lambda evaluation: evaluation.overall_score,
        )

        findings: list[ScenarioFinding] = []
        deltas: list[SystemDelta] = []
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

        for evaluation in system_evaluations:
            if evaluation.system.system_id != scenario.baseline_system_id:
                delta = round(
                    evaluation.overall_score - baseline_evaluation.overall_score,
                    4,
                )
                deltas.append(
                    SystemDelta(
                        system_id=evaluation.system.system_id,
                        delta_vs_baseline=delta,
                    )
                )
                if delta <= -self.config.regression_threshold:
                    add_finding(
                        category="BASELINE_REGRESSION",
                        severity="high",
                        related_ids=[
                            evaluation.system.system_id,
                            scenario.baseline_system_id,
                        ],
                        description=(
                            f"System `{evaluation.system.system_id}` scored {abs(delta):.2f} "
                            "below the baseline."
                        ),
                    )

            if evaluation.coverage < self.config.coverage_floor:
                add_finding(
                    category="COVERAGE_RISK",
                    severity="medium",
                    related_ids=[evaluation.system.system_id],
                    description=(
                        f"System `{evaluation.system.system_id}` covered only "
                        f"{evaluation.coverage:.0%} of the multimodal gallery."
                    ),
                )

            if evaluation.hard_negative_rate > self.config.hard_negative_ceiling:
                add_finding(
                    category="HARD_NEGATIVE_DRIFT",
                    severity="high",
                    related_ids=[evaluation.system.system_id],
                    description=(
                        f"System `{evaluation.system.system_id}` hit hard negatives on "
                        f"{evaluation.hard_negative_rate:.0%} of queries."
                    ),
                )

            for summary in evaluation.slice_summaries:
                if (
                    summary.slice_type == "direction"
                    and summary.recall_at_k < self.config.direction_recall_floor
                ):
                    add_finding(
                        category="DIRECTION_GAP",
                        severity="medium",
                        related_ids=[evaluation.system.system_id, summary.slice_value],
                        description=(
                            f"System `{evaluation.system.system_id}` reached only "
                            f"{summary.recall_at_k:.2f} Recall@K on `{summary.slice_value}`."
                        ),
                    )

                if (
                    summary.slice_type == "segment"
                    and summary.recall_at_k < self.config.segment_recall_floor
                ):
                    add_finding(
                        category="SEGMENT_DROP",
                        severity="medium",
                        related_ids=[evaluation.system.system_id, summary.slice_value],
                        description=(
                            f"System `{evaluation.system.system_id}` dropped to "
                            f"{summary.recall_at_k:.2f} Recall@K on segment `{summary.slice_value}`."
                        ),
                    )

        if best_evaluation.system.system_id != scenario.baseline_system_id:
            add_finding(
                category="WINNER",
                severity="low",
                related_ids=[best_evaluation.system.system_id],
                description=(
                    f"System `{best_evaluation.system.system_id}` delivered the best "
                    f"composite score at {best_evaluation.overall_score:.2f}."
                ),
            )

        metrics = summarize_scenario(
            system_evaluations=system_evaluations,
            baseline_score=baseline_evaluation.overall_score,
            best_score=best_evaluation.overall_score,
            best_system_id=best_evaluation.system.system_id,
        )
        return ScenarioResult(
            scenario=scenario,
            system_evaluations=system_evaluations,
            deltas=deltas,
            findings=findings,
            metrics=metrics,
        )

    def run_benchmark(self, benchmark: RetrievalBenchmark) -> ExperimentResult:
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
