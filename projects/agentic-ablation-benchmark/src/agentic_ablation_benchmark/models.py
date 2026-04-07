from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class VariantRun:
    variant_id: str
    prompt_strategy: str
    tool_policy: str
    retrieval_policy: str
    completed: bool
    quality_score: float
    tool_calls: int
    failed_calls: int
    recovered_failures: int
    loop_events: int
    latency_ms: int
    prompt_tokens: int
    completion_tokens: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BenchmarkTask:
    task_id: str
    name: str
    baseline_variant_id: str
    variants: list[VariantRun]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AblationBenchmark:
    benchmark_id: str
    description: str
    tasks: list[BenchmarkTask]


@dataclass(frozen=True)
class VariantScore:
    variant: VariantRun
    total_tokens: int
    completion_score: float
    quality_score: float
    recovery_score: float
    efficiency_score: float
    latency_score: float
    token_efficiency_score: float
    overall_score: float


@dataclass(frozen=True)
class VariantDelta:
    variant_id: str
    changed_factors: list[str]
    delta_vs_baseline: float


@dataclass(frozen=True)
class FactorSummary:
    factor_name: str
    factor_value: str
    comparison_count: int
    mean_delta: float
    win_rate: float


@dataclass(frozen=True)
class TaskFinding:
    finding_id: str
    category: str
    severity: str
    related_ids: list[str]
    description: str


@dataclass(frozen=True)
class TaskMetrics:
    variant_count: int
    completion_rate: float
    baseline_score: float
    best_score: float
    mean_score: float
    best_variant_id: str


@dataclass(frozen=True)
class AggregateMetrics:
    task_count: int
    variant_count: int
    mean_completion_rate: float
    mean_score: float
    mean_recovery_score: float
    mean_latency_score: float
    total_findings: int


@dataclass(frozen=True)
class TaskResult:
    task: BenchmarkTask
    scored_variants: list[VariantScore]
    deltas: list[VariantDelta]
    factor_summaries: list[FactorSummary]
    findings: list[TaskFinding]
    metrics: TaskMetrics


@dataclass(frozen=True)
class AblationConfig:
    experiment_name: str = "baseline"
    latency_budget_ms: int = 5000
    token_budget: int = 1300
    ideal_tool_calls: int = 6
    regression_threshold: float = 0.08
    loop_penalty: float = 0.08

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "AblationConfig":
        return cls(
            experiment_name=str(raw.get("experiment_name", cls.experiment_name)),
            latency_budget_ms=int(raw.get("latency_budget_ms", cls.latency_budget_ms)),
            token_budget=int(raw.get("token_budget", cls.token_budget)),
            ideal_tool_calls=int(raw.get("ideal_tool_calls", cls.ideal_tool_calls)),
            regression_threshold=float(
                raw.get("regression_threshold", cls.regression_threshold)
            ),
            loop_penalty=float(raw.get("loop_penalty", cls.loop_penalty)),
        )


@dataclass(frozen=True)
class ExperimentResult:
    benchmark_id: str
    benchmark_description: str
    config: AblationConfig
    tasks: list[TaskResult]
    aggregate_metrics: AggregateMetrics
    generated_at: str

