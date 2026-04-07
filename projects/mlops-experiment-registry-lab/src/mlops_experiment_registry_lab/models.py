from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExperimentRun:
    run_id: str
    model_name: str
    metrics: dict[str, float]
    parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RegistryBenchmark:
    benchmark_id: str
    description: str
    incumbent_run_id: str | None
    runs: list[ExperimentRun]


@dataclass(frozen=True)
class RegistryPolicy:
    experiment_name: str = "baseline-registry-policy"
    metric_name: str = "eval_f1"
    mode: str = "max"
    min_improvement: float = 0.01
    required_metadata: list[str] = field(
        default_factory=lambda: ["dataset_id", "code_sha", "created_at"]
    )
    blocked_tags: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "RegistryPolicy":
        return cls(
            experiment_name=str(raw.get("experiment_name", cls.experiment_name)),
            metric_name=str(raw.get("metric_name", cls.metric_name)),
            mode=str(raw.get("mode", cls.mode)),
            min_improvement=float(raw.get("min_improvement", cls.min_improvement)),
            required_metadata=[
                str(value) for value in raw.get("required_metadata", cls().required_metadata)
            ],
            blocked_tags=[str(value) for value in raw.get("blocked_tags", [])],
        )


@dataclass(frozen=True)
class RankedRun:
    run_id: str
    model_name: str
    metric_value: float
    rank: int
    warnings: list[str]


@dataclass(frozen=True)
class RegistryDecision:
    candidate_run_id: str | None
    incumbent_run_id: str | None
    promoted: bool
    metric_delta: float | None
    warnings: list[str]
    rationale: str


@dataclass(frozen=True)
class RegistryResult:
    benchmark_id: str
    benchmark_description: str
    policy: RegistryPolicy
    ranked_runs: list[RankedRun]
    decision: RegistryDecision
    generated_at: str
