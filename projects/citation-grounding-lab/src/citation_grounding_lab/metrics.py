from __future__ import annotations

from statistics import fmean

from .models import (
    CONTRADICTED,
    PARTIAL,
    SUPPORTED,
    AggregateMetrics,
    ClaimAssessment,
)


def summarize_assessments(assessments: list[ClaimAssessment]) -> AggregateMetrics:
    claim_count = len(assessments)
    if claim_count == 0:
        return AggregateMetrics(
            claim_count=0,
            supported_claims=0,
            partial_claims=0,
            unsupported_claims=0,
            contradicted_claims=0,
            citation_precision=1.0,
            support_rate=0.0,
            contradiction_rate=0.0,
            mean_support_score=0.0,
            faithfulness_score=0.0,
        )

    supported_claims = sum(assessment.label == SUPPORTED for assessment in assessments)
    partial_claims = sum(assessment.label == PARTIAL for assessment in assessments)
    contradicted_claims = sum(assessment.label == CONTRADICTED for assessment in assessments)
    unsupported_claims = claim_count - supported_claims - partial_claims - contradicted_claims

    citation_values = [
        assessment.citation_precision
        for assessment in assessments
        if assessment.claim.cited_doc_ids
    ]
    citation_precision = fmean(citation_values) if citation_values else 1.0
    support_rate = (supported_claims + (0.5 * partial_claims)) / claim_count
    contradiction_rate = contradicted_claims / claim_count
    mean_support_score = fmean(assessment.support_score for assessment in assessments)
    faithfulness_score = (
        (0.55 * support_rate)
        + (0.25 * citation_precision)
        + (0.20 * (1.0 - contradiction_rate))
    )

    return AggregateMetrics(
        claim_count=claim_count,
        supported_claims=supported_claims,
        partial_claims=partial_claims,
        unsupported_claims=unsupported_claims,
        contradicted_claims=contradicted_claims,
        citation_precision=round(citation_precision, 4),
        support_rate=round(support_rate, 4),
        contradiction_rate=round(contradiction_rate, 4),
        mean_support_score=round(mean_support_score, 4),
        faithfulness_score=round(max(0.0, min(1.0, faithfulness_score)), 4),
    )
