from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ContextItem:
    item_id: str
    title: str
    text: str
    estimated_tokens: int
    priority: int
    relevance: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AnswerSnapshot:
    snapshot_id: str
    budget_tokens: int
    answer: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StressCase:
    case_id: str
    question: str
    reference_answer: str
    context_items: list[ContextItem]
    answer_snapshots: list[AnswerSnapshot]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StressBenchmark:
    benchmark_id: str
    description: str
    cases: list[StressCase]


@dataclass(frozen=True)
class SnapshotFinding:
    finding_id: str
    category: str
    severity: str
    related_ids: list[str]
    description: str


@dataclass(frozen=True)
class SnapshotEvaluation:
    snapshot: AnswerSnapshot
    packed_context_ids: list[str]
    packed_tokens: int
    relevant_coverage: float
    noise_ratio: float
    reference_alignment: float
    answer_support: float
    unsupported_token_rate: float
    drift_score: float
    findings: list[SnapshotFinding]


@dataclass(frozen=True)
class CaseMetrics:
    snapshot_count: int
    mean_relevant_coverage: float
    mean_noise_ratio: float
    mean_reference_alignment: float
    mean_answer_support: float
    mean_unsupported_token_rate: float
    max_drift_score: float
    finding_count: int


@dataclass(frozen=True)
class AggregateMetrics:
    case_count: int
    snapshot_count: int
    mean_relevant_coverage: float
    mean_noise_ratio: float
    mean_reference_alignment: float
    mean_answer_support: float
    mean_unsupported_token_rate: float
    max_drift_score: float
    total_findings: int


@dataclass(frozen=True)
class CaseResult:
    case: StressCase
    evaluations: list[SnapshotEvaluation]
    metrics: CaseMetrics


@dataclass(frozen=True)
class StressConfig:
    experiment_name: str = "baseline"
    min_relevant_coverage: float = 0.65
    max_noise_ratio: float = 0.45
    drift_drop_threshold: float = 0.12
    unsupported_token_rate_threshold: float = 0.35

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "StressConfig":
        return cls(
            experiment_name=str(raw.get("experiment_name", cls.experiment_name)),
            min_relevant_coverage=float(
                raw.get("min_relevant_coverage", cls.min_relevant_coverage)
            ),
            max_noise_ratio=float(raw.get("max_noise_ratio", cls.max_noise_ratio)),
            drift_drop_threshold=float(
                raw.get("drift_drop_threshold", cls.drift_drop_threshold)
            ),
            unsupported_token_rate_threshold=float(
                raw.get(
                    "unsupported_token_rate_threshold",
                    cls.unsupported_token_rate_threshold,
                )
            ),
        )


@dataclass(frozen=True)
class ExperimentResult:
    benchmark_id: str
    benchmark_description: str
    config: StressConfig
    cases: list[CaseResult]
    aggregate_metrics: AggregateMetrics
    generated_at: str
