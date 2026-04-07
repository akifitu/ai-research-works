from __future__ import annotations

from dataclasses import dataclass

from .metrics import build_run_metrics
from .models import AuditConfig, AuditFinding, RunResult, ToolTraceStep, TraceRun
from .normalization import (
    is_empty_result,
    is_failure_result,
    normalize_tool_signature,
)


@dataclass
class PendingFailure:
    result_index: int
    tool_name: str
    signature: str
    step_ids: list[str]
    resolved: bool = False


class TraceAuditor:
    def __init__(self, config: AuditConfig):
        self.config = config

    def audit_run(self, run: TraceRun) -> RunResult:
        findings: list[AuditFinding] = []
        pending_failures: list[PendingFailure] = []

        tool_call_count = 0
        tool_result_count = 0
        success_count = 0
        failure_count = 0
        recovered_failure_count = 0
        redundant_tool_calls = 0
        loop_count = 0
        empty_result_count = 0
        high_latency_steps = 0

        last_tool_call: ToolTraceStep | None = None
        last_signature: str | None = None
        signature_streak = 0
        empty_signature: str | None = None
        empty_streak = 0

        finding_index = 1

        def add_finding(
            category: str, severity: str, title: str, step_ids: list[str], description: str
        ) -> None:
            nonlocal finding_index
            findings.append(
                AuditFinding(
                    finding_id=f"{run.run_id}-finding-{finding_index:02d}",
                    category=category,
                    severity=severity,
                    title=title,
                    step_ids=step_ids,
                    description=description,
                )
            )
            finding_index += 1

        for index, step in enumerate(run.steps):
            if step.duration_ms is not None and step.duration_ms >= self.config.latency_threshold_ms:
                high_latency_steps += 1
                add_finding(
                    category="LATENCY",
                    severity="medium",
                    title="High-latency step detected",
                    step_ids=[step.step_id],
                    description=(
                        f"Step `{step.step_id}` took {step.duration_ms} ms, which exceeds the "
                        f"{self.config.latency_threshold_ms} ms threshold."
                    ),
                )

            if step.kind == "tool_call":
                tool_call_count += 1
                signature = normalize_tool_signature(step)

                if signature == last_signature:
                    signature_streak += 1
                    redundant_tool_calls += 1
                    if signature_streak == self.config.loop_repeat_threshold:
                        loop_count += 1
                        add_finding(
                            category="LOOP",
                            severity="high",
                            title="Repeated tool call loop",
                            step_ids=[step.step_id],
                            description=(
                                f"The tool signature `{signature}` repeated "
                                f"{signature_streak} times without adaptation."
                            ),
                        )
                else:
                    last_signature = signature
                    signature_streak = 1

                last_tool_call = step
                continue

            if step.kind != "tool_result":
                continue

            tool_result_count += 1
            paired_signature = normalize_tool_signature(last_tool_call)
            paired_tool_name = (last_tool_call.tool_name or "unknown") if last_tool_call else "unknown"

            if is_failure_result(step):
                failure_count += 1
                pending_failures.append(
                    PendingFailure(
                        result_index=index,
                        tool_name=paired_tool_name,
                        signature=paired_signature,
                        step_ids=[value for value in [last_tool_call.step_id if last_tool_call else None, step.step_id] if value],
                    )
                )
                add_finding(
                    category="FAILURE",
                    severity="high",
                    title="Tool execution failed",
                    step_ids=[value for value in [last_tool_call.step_id if last_tool_call else None, step.step_id] if value],
                    description=(
                        f"Tool `{paired_tool_name}` returned a failure result: {step.content.strip()}"
                    ),
                )
                empty_signature = None
                empty_streak = 0
                continue

            success_count += 1

            if last_tool_call is not None:
                recovered_failure = self._recover_failure(
                    pending_failures=pending_failures,
                    current_index=index,
                    tool_name=paired_tool_name,
                    signature=paired_signature,
                )
                if recovered_failure is not None:
                    recovered_failure_count += 1
                    add_finding(
                        category="RECOVERY",
                        severity="low",
                        title="Failure recovered",
                        step_ids=recovered_failure.step_ids
                        + [value for value in [last_tool_call.step_id, step.step_id] if value],
                        description=(
                            f"A prior failure on `{paired_tool_name}` was followed by an adjusted "
                            f"successful action within the recovery window."
                        ),
                    )

            if is_empty_result(step):
                if paired_signature == empty_signature:
                    empty_streak += 1
                else:
                    empty_signature = paired_signature
                    empty_streak = 1

                if empty_streak == self.config.empty_result_threshold:
                    empty_result_count += 1
                    add_finding(
                        category="EMPTY_RESULT",
                        severity="medium",
                        title="Repeated empty tool output",
                        step_ids=[value for value in [last_tool_call.step_id if last_tool_call else None, step.step_id] if value],
                        description=(
                            f"The tool signature `{paired_signature}` produced "
                            f"{empty_streak} empty results in a row."
                        ),
                    )
            else:
                empty_signature = None
                empty_streak = 0

        metrics = build_run_metrics(
            step_count=len(run.steps),
            tool_call_count=tool_call_count,
            tool_result_count=tool_result_count,
            success_count=success_count,
            failure_count=failure_count,
            recovered_failure_count=recovered_failure_count,
            redundant_tool_calls=redundant_tool_calls,
            loop_count=loop_count,
            empty_result_count=empty_result_count,
            high_latency_steps=high_latency_steps,
        )
        return RunResult(run=run, findings=findings, metrics=metrics)

    def _recover_failure(
        self,
        *,
        pending_failures: list[PendingFailure],
        current_index: int,
        tool_name: str,
        signature: str,
    ) -> PendingFailure | None:
        for failure in pending_failures:
            if failure.resolved:
                continue
            if current_index - failure.result_index > self.config.recovery_window:
                continue
            if failure.tool_name != tool_name:
                continue
            if failure.signature == signature:
                continue

            failure.resolved = True
            return failure
        return None
