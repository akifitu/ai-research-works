from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolTraceStep:
    step_id: str
    kind: str
    content: str
    tool_name: str | None = None
    status: str | None = None
    duration_ms: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TraceRun:
    run_id: str
    task: str
    steps: list[ToolTraceStep]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TraceBenchmark:
    benchmark_id: str
    description: str
    runs: list[TraceRun]


@dataclass(frozen=True)
class AuditFinding:
    finding_id: str
    category: str
    severity: str
    title: str
    step_ids: list[str]
    description: str


@dataclass(frozen=True)
class RunMetrics:
    step_count: int
    tool_call_count: int
    tool_result_count: int
    success_count: int
    failure_count: int
    recovered_failure_count: int
    recovery_rate: float
    redundancy_rate: float
    loop_count: int
    empty_result_count: int
    high_latency_steps: int
    efficiency_score: float


@dataclass(frozen=True)
class AggregateMetrics:
    run_count: int
    total_steps: int
    total_failures: int
    total_loops: int
    total_empty_result_findings: int
    total_latency_steps: int
    mean_recovery_rate: float
    mean_redundancy_rate: float
    mean_efficiency_score: float


@dataclass(frozen=True)
class RunResult:
    run: TraceRun
    findings: list[AuditFinding]
    metrics: RunMetrics


@dataclass(frozen=True)
class AuditConfig:
    experiment_name: str = "baseline"
    loop_repeat_threshold: int = 3
    empty_result_threshold: int = 2
    recovery_window: int = 4
    latency_threshold_ms: int = 1200

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "AuditConfig":
        return cls(
            experiment_name=str(raw.get("experiment_name", cls.experiment_name)),
            loop_repeat_threshold=int(
                raw.get("loop_repeat_threshold", cls.loop_repeat_threshold)
            ),
            empty_result_threshold=int(
                raw.get("empty_result_threshold", cls.empty_result_threshold)
            ),
            recovery_window=int(raw.get("recovery_window", cls.recovery_window)),
            latency_threshold_ms=int(
                raw.get("latency_threshold_ms", cls.latency_threshold_ms)
            ),
        )


@dataclass(frozen=True)
class ExperimentResult:
    benchmark_id: str
    benchmark_description: str
    config: AuditConfig
    runs: list[RunResult]
    aggregate_metrics: AggregateMetrics
    generated_at: str
