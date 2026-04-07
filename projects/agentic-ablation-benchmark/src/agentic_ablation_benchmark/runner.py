from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from .metrics import summarize_benchmark, summarize_task
from .models import (
    AblationBenchmark,
    AblationConfig,
    ExperimentResult,
    FactorSummary,
    TaskFinding,
    TaskResult,
    VariantDelta,
)
from .scoring import changed_factors, score_variant


class ExperimentRunner:
    def __init__(self, config: AblationConfig):
        self.config = config

    def run_task(self, task) -> TaskResult:
        scored_variants = [score_variant(variant, self.config) for variant in task.variants]
        by_variant_id = {score.variant.variant_id: score for score in scored_variants}
        baseline_score = by_variant_id[task.baseline_variant_id]
        best_variant = max(scored_variants, key=lambda score: score.overall_score)

        deltas: list[VariantDelta] = []
        factor_bucket: dict[tuple[str, str], list[tuple[float, bool]]] = defaultdict(list)
        findings: list[TaskFinding] = []
        finding_index = 1

        def add_finding(category: str, severity: str, related_ids: list[str], description: str) -> None:
            nonlocal finding_index
            findings.append(
                TaskFinding(
                    finding_id=f"{task.task_id}-finding-{finding_index:02d}",
                    category=category,
                    severity=severity,
                    related_ids=related_ids,
                    description=description,
                )
            )
            finding_index += 1

        for score in scored_variants:
            if score.variant.variant_id == task.baseline_variant_id:
                continue

            delta = round(score.overall_score - baseline_score.overall_score, 4)
            factors = changed_factors(baseline_score.variant, score.variant)
            deltas.append(
                VariantDelta(
                    variant_id=score.variant.variant_id,
                    changed_factors=factors,
                    delta_vs_baseline=delta,
                )
            )
            for factor in factors:
                factor_name, factor_value = factor.split(":", 1)
                factor_bucket[(factor_name, factor_value)].append((delta, delta > 0.0))

            if delta <= -self.config.regression_threshold:
                add_finding(
                    category="REGRESSION",
                    severity="high",
                    related_ids=[score.variant.variant_id, task.baseline_variant_id],
                    description=(
                        f"Variant `{score.variant.variant_id}` underperformed baseline by {abs(delta):.2f}."
                    ),
                )

            if score.variant.loop_events > 0 or score.efficiency_score < 0.5:
                add_finding(
                    category="LOOP_RISK",
                    severity="medium",
                    related_ids=[score.variant.variant_id],
                    description=(
                        f"Variant `{score.variant.variant_id}` showed loop or tool-efficiency risk."
                    ),
                )

            if score.variant.failed_calls > 0 and score.recovery_score < 0.75:
                add_finding(
                    category="RECOVERY_GAP",
                    severity="high",
                    related_ids=[score.variant.variant_id],
                    description=(
                        f"Variant `{score.variant.variant_id}` recovered only {score.recovery_score:.0%} "
                        "of failures."
                    ),
                )

            if (
                score.total_tokens > self.config.token_budget
                or score.variant.latency_ms > self.config.latency_budget_ms
            ):
                add_finding(
                    category="COST_SPIKE",
                    severity="medium",
                    related_ids=[score.variant.variant_id],
                    description=(
                        f"Variant `{score.variant.variant_id}` exceeded the configured token or latency budget."
                    ),
                )

        if best_variant.variant.variant_id != task.baseline_variant_id:
            add_finding(
                category="WINNER",
                severity="low",
                related_ids=[best_variant.variant.variant_id],
                description=(
                    f"Variant `{best_variant.variant.variant_id}` delivered the top composite score "
                    f"at {best_variant.overall_score:.2f}."
                ),
            )

        factor_summaries = [
            FactorSummary(
                factor_name=factor_name,
                factor_value=factor_value,
                comparison_count=len(entries),
                mean_delta=round(sum(delta for delta, _ in entries) / len(entries), 4),
                win_rate=round(sum(win for _, win in entries) / len(entries), 4),
            )
            for (factor_name, factor_value), entries in sorted(factor_bucket.items())
        ]

        metrics = summarize_task(
            scored_variants=scored_variants,
            baseline_score=baseline_score.overall_score,
            best_score=best_variant.overall_score,
            best_variant_id=best_variant.variant.variant_id,
        )
        return TaskResult(
            task=task,
            scored_variants=scored_variants,
            deltas=deltas,
            factor_summaries=factor_summaries,
            findings=findings,
            metrics=metrics,
        )

    def run_benchmark(self, benchmark: AblationBenchmark) -> ExperimentResult:
        task_results = [self.run_task(task) for task in benchmark.tasks]
        aggregate_metrics = summarize_benchmark(task_results)
        generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        return ExperimentResult(
            benchmark_id=benchmark.benchmark_id,
            benchmark_description=benchmark.description,
            config=self.config,
            tasks=task_results,
            aggregate_metrics=aggregate_metrics,
            generated_at=generated_at,
        )

