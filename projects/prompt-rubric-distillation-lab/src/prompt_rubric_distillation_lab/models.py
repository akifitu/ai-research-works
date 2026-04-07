from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RubricCriterion:
    criterion_id: str
    text: str
    weight: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Rubric:
    rubric_id: str
    task: str
    criteria: list[RubricCriterion]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RubricBenchmark:
    benchmark_id: str
    description: str
    rubrics: list[Rubric]


@dataclass(frozen=True)
class DistillationFinding:
    finding_id: str
    category: str
    severity: str
    criterion_id: str | None
    description: str


@dataclass(frozen=True)
class DistilledCriterion:
    criterion_id: str
    source_text: str
    dimension: str
    scale_type: str
    normalized_weight: float
    ambiguity_flags: list[str]
    specificity_score: float
    checklist_questions: list[str]
    scoring_anchors: list[str]


@dataclass(frozen=True)
class RubricMetrics:
    criterion_count: int
    ambiguity_rate: float
    mean_specificity_score: float
    explicit_weight_coverage: float
    dimension_diversity: int


@dataclass(frozen=True)
class AggregateMetrics:
    rubric_count: int
    total_criteria: int
    mean_ambiguity_rate: float
    mean_specificity_score: float
    mean_explicit_weight_coverage: float
    total_findings: int


@dataclass(frozen=True)
class RubricResult:
    rubric: Rubric
    distilled_criteria: list[DistilledCriterion]
    findings: list[DistillationFinding]
    metrics: RubricMetrics


@dataclass(frozen=True)
class DistillationConfig:
    experiment_name: str = "baseline"
    default_scale_levels: int = 5
    ambiguity_penalty: float = 0.12
    explicit_requirement_bonus: float = 0.08
    minimum_weight_floor: float = 0.05

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "DistillationConfig":
        return cls(
            experiment_name=str(raw.get("experiment_name", cls.experiment_name)),
            default_scale_levels=int(raw.get("default_scale_levels", cls.default_scale_levels)),
            ambiguity_penalty=float(raw.get("ambiguity_penalty", cls.ambiguity_penalty)),
            explicit_requirement_bonus=float(
                raw.get(
                    "explicit_requirement_bonus",
                    cls.explicit_requirement_bonus,
                )
            ),
            minimum_weight_floor=float(
                raw.get("minimum_weight_floor", cls.minimum_weight_floor)
            ),
        )


@dataclass(frozen=True)
class ExperimentResult:
    benchmark_id: str
    benchmark_description: str
    config: DistillationConfig
    rubrics: list[RubricResult]
    aggregate_metrics: AggregateMetrics
    generated_at: str
