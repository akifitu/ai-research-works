from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AssetCard:
    asset_id: str
    modality: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievalSystem:
    system_id: str
    family: str
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievalQuery:
    query_id: str
    direction: str
    segment: str
    relevant_target_ids: list[str]
    hard_negative_ids: list[str]
    predictions: dict[str, list[str]]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievalScenario:
    scenario_id: str
    name: str
    k: int
    baseline_system_id: str
    assets: list[AssetCard]
    systems: list[RetrievalSystem]
    queries: list[RetrievalQuery]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievalBenchmark:
    benchmark_id: str
    description: str
    scenarios: list[RetrievalScenario]


@dataclass(frozen=True)
class SliceSummary:
    slice_type: str
    slice_value: str
    query_count: int
    recall_at_k: float
    mrr: float
    top1_accuracy: float
    hard_negative_rate: float


@dataclass(frozen=True)
class SystemEvaluation:
    system: RetrievalSystem
    query_count: int
    recall_at_k: float
    mrr: float
    top1_accuracy: float
    median_rank: float
    coverage: float
    hard_negative_rate: float
    overall_score: float
    slice_summaries: list[SliceSummary]


@dataclass(frozen=True)
class SystemDelta:
    system_id: str
    delta_vs_baseline: float


@dataclass(frozen=True)
class ScenarioFinding:
    finding_id: str
    category: str
    severity: str
    related_ids: list[str]
    description: str


@dataclass(frozen=True)
class ScenarioMetrics:
    system_count: int
    baseline_score: float
    best_score: float
    mean_recall_at_k: float
    mean_coverage: float
    best_system_id: str


@dataclass(frozen=True)
class AggregateMetrics:
    scenario_count: int
    system_count: int
    mean_recall_at_k: float
    mean_mrr: float
    mean_coverage: float
    mean_hard_negative_rate: float
    total_findings: int


@dataclass(frozen=True)
class ScenarioResult:
    scenario: RetrievalScenario
    system_evaluations: list[SystemEvaluation]
    deltas: list[SystemDelta]
    findings: list[ScenarioFinding]
    metrics: ScenarioMetrics


@dataclass(frozen=True)
class RetrievalEvalConfig:
    experiment_name: str = "baseline"
    k: int = 3
    coverage_floor: float = 0.55
    hard_negative_ceiling: float = 0.35
    direction_recall_floor: float = 0.45
    segment_recall_floor: float = 0.40
    regression_threshold: float = 0.08

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "RetrievalEvalConfig":
        return cls(
            experiment_name=str(raw.get("experiment_name", cls.experiment_name)),
            k=int(raw.get("k", cls.k)),
            coverage_floor=float(raw.get("coverage_floor", cls.coverage_floor)),
            hard_negative_ceiling=float(
                raw.get("hard_negative_ceiling", cls.hard_negative_ceiling)
            ),
            direction_recall_floor=float(
                raw.get("direction_recall_floor", cls.direction_recall_floor)
            ),
            segment_recall_floor=float(
                raw.get("segment_recall_floor", cls.segment_recall_floor)
            ),
            regression_threshold=float(
                raw.get("regression_threshold", cls.regression_threshold)
            ),
        )


@dataclass(frozen=True)
class ExperimentResult:
    benchmark_id: str
    benchmark_description: str
    config: RetrievalEvalConfig
    scenarios: list[ScenarioResult]
    aggregate_metrics: AggregateMetrics
    generated_at: str
