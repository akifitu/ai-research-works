from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CatalogItem:
    item_id: str
    is_long_tail: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RankingSystem:
    system_id: str
    family: str
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RelevanceJudgment:
    item_id: str
    grade: int


@dataclass(frozen=True)
class RankingQuery:
    query_id: str
    segment: str
    relevant_items: list[RelevanceJudgment]
    predictions: dict[str, list[str]]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RankingScenario:
    scenario_id: str
    name: str
    k: int
    baseline_system_id: str
    catalog: list[CatalogItem]
    systems: list[RankingSystem]
    queries: list[RankingQuery]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RankingBenchmark:
    benchmark_id: str
    description: str
    scenarios: list[RankingScenario]


@dataclass(frozen=True)
class SegmentSummary:
    segment: str
    query_count: int
    ndcg_at_k: float
    map_at_k: float
    hit_rate: float
    long_tail_share: float


@dataclass(frozen=True)
class SystemEvaluation:
    system: RankingSystem
    query_count: int
    ndcg_at_k: float
    map_at_k: float
    precision_at_k: float
    recall_at_k: float
    hit_rate: float
    coverage: float
    long_tail_share: float
    overall_score: float
    segment_summaries: list[SegmentSummary]


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
    mean_ndcg_at_k: float
    mean_coverage: float
    best_system_id: str


@dataclass(frozen=True)
class AggregateMetrics:
    scenario_count: int
    system_count: int
    mean_ndcg_at_k: float
    mean_map_at_k: float
    mean_coverage: float
    mean_long_tail_share: float
    total_findings: int


@dataclass(frozen=True)
class ScenarioResult:
    scenario: RankingScenario
    system_evaluations: list[SystemEvaluation]
    deltas: list[SystemDelta]
    findings: list[ScenarioFinding]
    metrics: ScenarioMetrics


@dataclass(frozen=True)
class RankingEvalConfig:
    experiment_name: str = "baseline"
    k: int = 5
    coverage_floor: float = 0.45
    long_tail_floor: float = 0.12
    cold_start_ndcg_floor: float = 0.45
    regression_threshold: float = 0.08

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "RankingEvalConfig":
        return cls(
            experiment_name=str(raw.get("experiment_name", cls.experiment_name)),
            k=int(raw.get("k", cls.k)),
            coverage_floor=float(raw.get("coverage_floor", cls.coverage_floor)),
            long_tail_floor=float(raw.get("long_tail_floor", cls.long_tail_floor)),
            cold_start_ndcg_floor=float(
                raw.get("cold_start_ndcg_floor", cls.cold_start_ndcg_floor)
            ),
            regression_threshold=float(
                raw.get("regression_threshold", cls.regression_threshold)
            ),
        )


@dataclass(frozen=True)
class ExperimentResult:
    benchmark_id: str
    benchmark_description: str
    config: RankingEvalConfig
    scenarios: list[ScenarioResult]
    aggregate_metrics: AggregateMetrics
    generated_at: str
