from __future__ import annotations

from datetime import datetime, timezone

from .drift import consistency_ratio, packed_support_ratio, token_overlap_ratio, unsupported_token_rate
from .metrics import summarize_benchmark, summarize_case
from .models import (
    CaseResult,
    ExperimentResult,
    SnapshotEvaluation,
    SnapshotFinding,
    StressBenchmark,
    StressCase,
    StressConfig,
)
from .packing import noise_ratio, pack_context, packed_tokens, relevant_coverage


class ExperimentRunner:
    def __init__(self, config: StressConfig):
        self.config = config

    def run_case(self, case: StressCase) -> CaseResult:
        evaluations: list[SnapshotEvaluation] = []
        previous_alignment: float | None = None
        previous_answer: str | None = None
        finding_index = 1

        for snapshot in sorted(case.answer_snapshots, key=lambda item: item.budget_tokens):
            packed_items = pack_context(case.context_items, snapshot.budget_tokens)
            coverage = relevant_coverage(case.context_items, packed_items)
            dilution = noise_ratio(packed_items)
            alignment = token_overlap_ratio(snapshot.answer, case.reference_answer)
            support = packed_support_ratio(snapshot.answer, packed_items)
            unsupported_rate = unsupported_token_rate(snapshot.answer, packed_items)
            if previous_answer is None:
                drift_score = 1.0 - alignment
            else:
                drift_score = 1.0 - (
                    (0.55 * alignment) + (0.45 * consistency_ratio(snapshot.answer, previous_answer))
                )

            findings: list[SnapshotFinding] = []

            def add_finding(
                category: str,
                severity: str,
                related_ids: list[str],
                description: str,
            ) -> None:
                nonlocal finding_index
                findings.append(
                    SnapshotFinding(
                        finding_id=f"{case.case_id}-finding-{finding_index:02d}",
                        category=category,
                        severity=severity,
                        related_ids=related_ids,
                        description=description,
                    )
                )
                finding_index += 1

            packed_ids = [item.item_id for item in packed_items]
            if coverage < self.config.min_relevant_coverage:
                missing_ids = [
                    item.item_id
                    for item in case.context_items
                    if item.relevance and item.item_id not in packed_ids
                ]
                add_finding(
                    category="OVERFLOW",
                    severity="high",
                    related_ids=[snapshot.snapshot_id] + missing_ids,
                    description=(
                        f"Relevant coverage fell to {coverage:.2f}, leaving important context out of "
                        f"the {snapshot.budget_tokens}-token budget."
                    ),
                )

            if dilution > self.config.max_noise_ratio:
                add_finding(
                    category="DILUTION",
                    severity="medium",
                    related_ids=[snapshot.snapshot_id] + packed_ids,
                    description=(
                        f"Noise ratio reached {dilution:.2f}, meaning irrelevant context dominated "
                        "too much of the packed window."
                    ),
                )

            if unsupported_rate > self.config.unsupported_token_rate_threshold:
                add_finding(
                    category="UNSUPPORTED_INSERTION",
                    severity="high",
                    related_ids=[snapshot.snapshot_id] + packed_ids,
                    description=(
                        f"The answer introduced unsupported content at a rate of {unsupported_rate:.2f} "
                        "relative to the packed context."
                    ),
                )

            if (
                previous_alignment is not None
                and (previous_alignment - alignment) >= self.config.drift_drop_threshold
            ):
                add_finding(
                    category="DRIFT",
                    severity="high",
                    related_ids=[snapshot.snapshot_id],
                    description=(
                        f"Reference alignment dropped from {previous_alignment:.2f} to {alignment:.2f} "
                        "when the budget increased."
                    ),
                )

            evaluations.append(
                SnapshotEvaluation(
                    snapshot=snapshot,
                    packed_context_ids=packed_ids,
                    packed_tokens=packed_tokens(packed_items),
                    relevant_coverage=round(coverage, 4),
                    noise_ratio=round(dilution, 4),
                    reference_alignment=round(alignment, 4),
                    answer_support=round(support, 4),
                    unsupported_token_rate=round(unsupported_rate, 4),
                    drift_score=round(max(0.0, min(1.0, drift_score)), 4),
                    findings=findings,
                )
            )
            previous_alignment = alignment
            previous_answer = snapshot.answer

        return CaseResult(
            case=case,
            evaluations=evaluations,
            metrics=summarize_case(evaluations),
        )

    def run_benchmark(self, benchmark: StressBenchmark) -> ExperimentResult:
        case_results = [self.run_case(case) for case in benchmark.cases]
        aggregate_metrics = summarize_benchmark(case_results)
        generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        return ExperimentResult(
            benchmark_id=benchmark.benchmark_id,
            benchmark_description=benchmark.description,
            config=self.config,
            cases=case_results,
            aggregate_metrics=aggregate_metrics,
            generated_at=generated_at,
        )
