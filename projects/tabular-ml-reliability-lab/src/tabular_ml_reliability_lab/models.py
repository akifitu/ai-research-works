from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


Row = dict[str, Any]


@dataclass(frozen=True)
class TabularBenchmark:
    benchmark_id: str
    description: str
    baseline_rows: list[Row]
    current_rows: list[Row]


@dataclass(frozen=True)
class ReliabilityConfig:
    experiment_name: str = "baseline-tabular-reliability"
    mean_shift_threshold: float = 0.30
    missing_rate_delta_threshold: float = 0.20
    categorical_overlap_threshold: float = 0.50
    target_column: str = "target"

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ReliabilityConfig":
        return cls(
            experiment_name=str(raw.get("experiment_name", cls.experiment_name)),
            mean_shift_threshold=float(
                raw.get("mean_shift_threshold", cls.mean_shift_threshold)
            ),
            missing_rate_delta_threshold=float(
                raw.get("missing_rate_delta_threshold", cls.missing_rate_delta_threshold)
            ),
            categorical_overlap_threshold=float(
                raw.get("categorical_overlap_threshold", cls.categorical_overlap_threshold)
            ),
            target_column=str(raw.get("target_column", cls.target_column)),
        )


@dataclass(frozen=True)
class FeatureProfile:
    name: str
    kind: str
    row_count: int
    missing_rate: float
    distinct_count: int
    mean: float | None = None
    top_values: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class DriftFinding:
    feature: str
    kind: str
    risk_level: str
    missing_rate_delta: float
    mean_shift: float | None
    categorical_overlap: float | None
    rationale: str


@dataclass(frozen=True)
class ReliabilityResult:
    benchmark_id: str
    benchmark_description: str
    config: ReliabilityConfig
    baseline_profile: list[FeatureProfile]
    current_profile: list[FeatureProfile]
    drift_findings: list[DriftFinding]
    leakage_candidates: list[str]
    high_risk_feature_count: int
    generated_at: str
