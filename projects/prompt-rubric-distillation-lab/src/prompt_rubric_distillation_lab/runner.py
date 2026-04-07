from __future__ import annotations

from datetime import datetime, timezone

from .distillation import (
    ambiguity_flags,
    checklist_questions,
    infer_dimension,
    infer_scale_type,
    normalize_weights,
    scoring_anchors,
    specificity_score,
)
from .metrics import summarize_benchmark, summarize_rubric
from .models import (
    DistillationConfig,
    DistillationFinding,
    DistilledCriterion,
    ExperimentResult,
    Rubric,
    RubricBenchmark,
    RubricResult,
)


class ExperimentRunner:
    def __init__(self, config: DistillationConfig):
        self.config = config

    def run_rubric(self, rubric: Rubric) -> RubricResult:
        dimensions = {
            criterion.criterion_id: infer_dimension(criterion.text) for criterion in rubric.criteria
        }
        normalized_weights = normalize_weights(rubric.criteria, dimensions, self.config)
        explicit_weight_coverage = (
            sum(criterion.weight is not None for criterion in rubric.criteria) / len(rubric.criteria)
            if rubric.criteria
            else 0.0
        )

        findings: list[DistillationFinding] = []
        distilled_criteria: list[DistilledCriterion] = []
        finding_index = 1

        def add_finding(
            category: str,
            severity: str,
            criterion_id: str | None,
            description: str,
        ) -> None:
            nonlocal finding_index
            findings.append(
                DistillationFinding(
                    finding_id=f"{rubric.rubric_id}-finding-{finding_index:02d}",
                    category=category,
                    severity=severity,
                    criterion_id=criterion_id,
                    description=description,
                )
            )
            finding_index += 1

        if 0.0 < explicit_weight_coverage < 1.0:
            add_finding(
                category="WEIGHT_GAP",
                severity="medium",
                criterion_id=None,
                description=(
                    "This rubric mixes explicit and implicit criterion weights, so normalization "
                    "was required to build a coherent scorecard."
                ),
            )

        for criterion in rubric.criteria:
            flags = ambiguity_flags(criterion.text)
            dimension = dimensions[criterion.criterion_id]
            scale_type = infer_scale_type(criterion.text)
            specificity = specificity_score(criterion.text, self.config)

            if flags:
                add_finding(
                    category="AMBIGUITY",
                    severity="medium",
                    criterion_id=criterion.criterion_id,
                    description=(
                        f"Criterion `{criterion.criterion_id}` contains vague terms: "
                        f"{', '.join(flags)}."
                    ),
                )

            if dimension == "general_quality":
                add_finding(
                    category="GENERAL_CRITERION",
                    severity="low",
                    criterion_id=criterion.criterion_id,
                    description=(
                        f"Criterion `{criterion.criterion_id}` did not map strongly to a known "
                        "evaluation dimension."
                    ),
                )

            distilled_criteria.append(
                DistilledCriterion(
                    criterion_id=criterion.criterion_id,
                    source_text=criterion.text,
                    dimension=dimension,
                    scale_type=scale_type,
                    normalized_weight=normalized_weights[criterion.criterion_id],
                    ambiguity_flags=flags,
                    specificity_score=round(specificity, 4),
                    checklist_questions=checklist_questions(dimension, criterion.text),
                    scoring_anchors=scoring_anchors(
                        scale_type,
                        dimension,
                        self.config.default_scale_levels,
                    ),
                )
            )

        return RubricResult(
            rubric=rubric,
            distilled_criteria=distilled_criteria,
            findings=findings,
            metrics=summarize_rubric(distilled_criteria, explicit_weight_coverage),
        )

    def run_benchmark(self, benchmark: RubricBenchmark) -> ExperimentResult:
        rubric_results = [self.run_rubric(rubric) for rubric in benchmark.rubrics]
        aggregate_metrics = summarize_benchmark(rubric_results)
        generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        return ExperimentResult(
            benchmark_id=benchmark.benchmark_id,
            benchmark_description=benchmark.description,
            config=self.config,
            rubrics=rubric_results,
            aggregate_metrics=aggregate_metrics,
            generated_at=generated_at,
        )
