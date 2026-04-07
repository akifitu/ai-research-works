from __future__ import annotations

from statistics import fmean

from .models import AggregateMetrics, CaseMetrics, CaseResult


def summarize_case(
    *,
    hop_supports: list[float],
    bridge_supports: list[float],
    conclusion_support: float,
    mapped_document_coverage: float,
    finding_count: int,
) -> CaseMetrics:
    return CaseMetrics(
        hop_count=len(hop_supports),
        mean_hop_support=round(fmean(hop_supports), 4) if hop_supports else 0.0,
        mean_bridge_support=round(fmean(bridge_supports), 4) if bridge_supports else 0.0,
        conclusion_support=round(conclusion_support, 4),
        mapped_document_coverage=round(mapped_document_coverage, 4),
        finding_count=finding_count,
    )


def summarize_benchmark(case_results: list[CaseResult]) -> AggregateMetrics:
    if not case_results:
        return AggregateMetrics(
            case_count=0,
            total_hops=0,
            mean_hop_support=0.0,
            mean_bridge_support=0.0,
            mean_conclusion_support=0.0,
            mean_mapped_document_coverage=0.0,
            total_findings=0,
        )

    return AggregateMetrics(
        case_count=len(case_results),
        total_hops=sum(result.metrics.hop_count for result in case_results),
        mean_hop_support=round(
            fmean(result.metrics.mean_hop_support for result in case_results), 4
        ),
        mean_bridge_support=round(
            fmean(result.metrics.mean_bridge_support for result in case_results), 4
        ),
        mean_conclusion_support=round(
            fmean(result.metrics.conclusion_support for result in case_results), 4
        ),
        mean_mapped_document_coverage=round(
            fmean(result.metrics.mapped_document_coverage for result in case_results), 4
        ),
        total_findings=sum(len(result.findings) for result in case_results),
    )
