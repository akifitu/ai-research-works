from __future__ import annotations

from statistics import fmean

from .models import AggregateMetrics, CaseMetrics, CaseResult, SnapshotEvaluation


def summarize_case(evaluations: list[SnapshotEvaluation]) -> CaseMetrics:
    if not evaluations:
        return CaseMetrics(
            snapshot_count=0,
            mean_relevant_coverage=0.0,
            mean_noise_ratio=0.0,
            mean_reference_alignment=0.0,
            mean_answer_support=0.0,
            mean_unsupported_token_rate=0.0,
            max_drift_score=0.0,
            finding_count=0,
        )

    return CaseMetrics(
        snapshot_count=len(evaluations),
        mean_relevant_coverage=round(fmean(item.relevant_coverage for item in evaluations), 4),
        mean_noise_ratio=round(fmean(item.noise_ratio for item in evaluations), 4),
        mean_reference_alignment=round(
            fmean(item.reference_alignment for item in evaluations), 4
        ),
        mean_answer_support=round(fmean(item.answer_support for item in evaluations), 4),
        mean_unsupported_token_rate=round(
            fmean(item.unsupported_token_rate for item in evaluations), 4
        ),
        max_drift_score=round(max(item.drift_score for item in evaluations), 4),
        finding_count=sum(len(item.findings) for item in evaluations),
    )


def summarize_benchmark(case_results: list[CaseResult]) -> AggregateMetrics:
    if not case_results:
        return AggregateMetrics(
            case_count=0,
            snapshot_count=0,
            mean_relevant_coverage=0.0,
            mean_noise_ratio=0.0,
            mean_reference_alignment=0.0,
            mean_answer_support=0.0,
            mean_unsupported_token_rate=0.0,
            max_drift_score=0.0,
            total_findings=0,
        )

    all_evaluations = [
        evaluation
        for case_result in case_results
        for evaluation in case_result.evaluations
    ]
    return AggregateMetrics(
        case_count=len(case_results),
        snapshot_count=len(all_evaluations),
        mean_relevant_coverage=round(
            fmean(item.relevant_coverage for item in all_evaluations), 4
        ),
        mean_noise_ratio=round(fmean(item.noise_ratio for item in all_evaluations), 4),
        mean_reference_alignment=round(
            fmean(item.reference_alignment for item in all_evaluations), 4
        ),
        mean_answer_support=round(fmean(item.answer_support for item in all_evaluations), 4),
        mean_unsupported_token_rate=round(
            fmean(item.unsupported_token_rate for item in all_evaluations), 4
        ),
        max_drift_score=round(max(item.drift_score for item in all_evaluations), 4),
        total_findings=sum(len(item.findings) for item in all_evaluations),
    )
