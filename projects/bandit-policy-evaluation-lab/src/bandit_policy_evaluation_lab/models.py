from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PolicyCard:
    policy_id: str
    family: str
    exploration_rate: float
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LoggedEvent:
    event_id: str
    action_taken: str
    reward: float
    oracle_reward: float
    logging_propensity: float
    segment: str
    policy_support: dict[str, float]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    name: str
    baseline_policy_id: str
    policies: list[PolicyCard]
    events: list[LoggedEvent]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BanditBenchmark:
    benchmark_id: str
    description: str
    scenarios: list[Scenario]


@dataclass(frozen=True)
class SegmentSummary:
    segment: str
    event_count: int
    support_rate: float
    ips_reward: float
    snips_reward: float
    regret_estimate: float


@dataclass(frozen=True)
class PolicyEvaluation:
    policy: PolicyCard
    event_count: int
    support_rate: float
    ips_reward: float
    snips_reward: float
    effective_sample_ratio: float
    max_weight: float
    regret_estimate: float
    overall_score: float
    segment_summaries: list[SegmentSummary]


@dataclass(frozen=True)
class PolicyDelta:
    policy_id: str
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
    policy_count: int
    baseline_score: float
    best_score: float
    mean_score: float
    mean_support_rate: float
    best_policy_id: str


@dataclass(frozen=True)
class AggregateMetrics:
    scenario_count: int
    policy_count: int
    mean_snips_reward: float
    mean_support_rate: float
    mean_effective_sample_ratio: float
    mean_regret_estimate: float
    total_findings: int


@dataclass(frozen=True)
class ScenarioResult:
    scenario: Scenario
    policy_evaluations: list[PolicyEvaluation]
    deltas: list[PolicyDelta]
    findings: list[ScenarioFinding]
    metrics: ScenarioMetrics


@dataclass(frozen=True)
class PolicyEvalConfig:
    experiment_name: str = "baseline"
    weight_clip: float = 4.0
    support_floor: float = 0.8
    min_effective_sample_ratio: float = 0.45
    regret_alert_threshold: float = 0.18
    segment_regret_threshold: float = 0.25
    regression_threshold: float = 0.08

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "PolicyEvalConfig":
        return cls(
            experiment_name=str(raw.get("experiment_name", cls.experiment_name)),
            weight_clip=float(raw.get("weight_clip", cls.weight_clip)),
            support_floor=float(raw.get("support_floor", cls.support_floor)),
            min_effective_sample_ratio=float(
                raw.get(
                    "min_effective_sample_ratio",
                    cls.min_effective_sample_ratio,
                )
            ),
            regret_alert_threshold=float(
                raw.get("regret_alert_threshold", cls.regret_alert_threshold)
            ),
            segment_regret_threshold=float(
                raw.get("segment_regret_threshold", cls.segment_regret_threshold)
            ),
            regression_threshold=float(
                raw.get("regression_threshold", cls.regression_threshold)
            ),
        )


@dataclass(frozen=True)
class ExperimentResult:
    benchmark_id: str
    benchmark_description: str
    config: PolicyEvalConfig
    scenarios: list[ScenarioResult]
    aggregate_metrics: AggregateMetrics
    generated_at: str
