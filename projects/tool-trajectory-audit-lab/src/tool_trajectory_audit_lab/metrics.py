from __future__ import annotations

from statistics import fmean

from .models import AggregateMetrics, RunResult, RunMetrics


def build_run_metrics(
    *,
    step_count: int,
    tool_call_count: int,
    tool_result_count: int,
    success_count: int,
    failure_count: int,
    recovered_failure_count: int,
    redundant_tool_calls: int,
    loop_count: int,
    empty_result_count: int,
    high_latency_steps: int,
) -> RunMetrics:
    recovery_rate = recovered_failure_count / failure_count if failure_count else 1.0
    redundancy_rate = redundant_tool_calls / tool_call_count if tool_call_count else 0.0
    success_rate = success_count / tool_result_count if tool_result_count else 1.0
    latency_rate = high_latency_steps / step_count if step_count else 0.0
    efficiency_score = (
        (0.35 * success_rate)
        + (0.25 * recovery_rate)
        + (0.25 * (1.0 - redundancy_rate))
        + (0.15 * (1.0 - latency_rate))
    )
    efficiency_score = max(0.0, min(1.0, efficiency_score))

    return RunMetrics(
        step_count=step_count,
        tool_call_count=tool_call_count,
        tool_result_count=tool_result_count,
        success_count=success_count,
        failure_count=failure_count,
        recovered_failure_count=recovered_failure_count,
        recovery_rate=round(recovery_rate, 4),
        redundancy_rate=round(redundancy_rate, 4),
        loop_count=loop_count,
        empty_result_count=empty_result_count,
        high_latency_steps=high_latency_steps,
        efficiency_score=round(efficiency_score, 4),
    )


def summarize_runs(run_results: list[RunResult]) -> AggregateMetrics:
    if not run_results:
        return AggregateMetrics(
            run_count=0,
            total_steps=0,
            total_failures=0,
            total_loops=0,
            total_empty_result_findings=0,
            total_latency_steps=0,
            mean_recovery_rate=0.0,
            mean_redundancy_rate=0.0,
            mean_efficiency_score=0.0,
        )

    metrics = [run_result.metrics for run_result in run_results]
    return AggregateMetrics(
        run_count=len(run_results),
        total_steps=sum(item.step_count for item in metrics),
        total_failures=sum(item.failure_count for item in metrics),
        total_loops=sum(item.loop_count for item in metrics),
        total_empty_result_findings=sum(item.empty_result_count for item in metrics),
        total_latency_steps=sum(item.high_latency_steps for item in metrics),
        mean_recovery_rate=round(fmean(item.recovery_rate for item in metrics), 4),
        mean_redundancy_rate=round(fmean(item.redundancy_rate for item in metrics), 4),
        mean_efficiency_score=round(fmean(item.efficiency_score for item in metrics), 4),
    )
