from __future__ import annotations

from statistics import fmean

from .models import AggregateMetrics, DistilledCriterion, RubricMetrics, RubricResult


def summarize_rubric(
    distilled_criteria: list[DistilledCriterion],
    explicit_weight_coverage: float,
) -> RubricMetrics:
    if not distilled_criteria:
        return RubricMetrics(
            criterion_count=0,
            ambiguity_rate=0.0,
            mean_specificity_score=0.0,
            explicit_weight_coverage=explicit_weight_coverage,
            dimension_diversity=0,
        )

    criteria_with_ambiguity = sum(bool(item.ambiguity_flags) for item in distilled_criteria)
    return RubricMetrics(
        criterion_count=len(distilled_criteria),
        ambiguity_rate=round(criteria_with_ambiguity / len(distilled_criteria), 4),
        mean_specificity_score=round(
            fmean(item.specificity_score for item in distilled_criteria), 4
        ),
        explicit_weight_coverage=round(explicit_weight_coverage, 4),
        dimension_diversity=len({item.dimension for item in distilled_criteria}),
    )


def summarize_benchmark(rubric_results: list[RubricResult]) -> AggregateMetrics:
    if not rubric_results:
        return AggregateMetrics(
            rubric_count=0,
            total_criteria=0,
            mean_ambiguity_rate=0.0,
            mean_specificity_score=0.0,
            mean_explicit_weight_coverage=0.0,
            total_findings=0,
        )

    return AggregateMetrics(
        rubric_count=len(rubric_results),
        total_criteria=sum(result.metrics.criterion_count for result in rubric_results),
        mean_ambiguity_rate=round(
            fmean(result.metrics.ambiguity_rate for result in rubric_results), 4
        ),
        mean_specificity_score=round(
            fmean(result.metrics.mean_specificity_score for result in rubric_results), 4
        ),
        mean_explicit_weight_coverage=round(
            fmean(result.metrics.explicit_weight_coverage for result in rubric_results), 4
        ),
        total_findings=sum(len(result.findings) for result in rubric_results),
    )
