from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import AuditConfig, ExperimentResult, ToolTraceStep, TraceBenchmark, TraceRun


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_benchmark(path: str | Path) -> TraceBenchmark:
    raw = _load_json(path)
    runs = [
        TraceRun(
            run_id=str(run["run_id"]),
            task=str(run["task"]),
            steps=[
                ToolTraceStep(
                    step_id=str(step["step_id"]),
                    kind=str(step["kind"]),
                    content=str(step.get("content", "")),
                    tool_name=(
                        str(step["tool_name"]) if step.get("tool_name") is not None else None
                    ),
                    status=str(step["status"]) if step.get("status") is not None else None,
                    duration_ms=(
                        int(step["duration_ms"])
                        if step.get("duration_ms") is not None
                        else None
                    ),
                    metadata=dict(step.get("metadata", {})),
                )
                for step in run.get("steps", [])
            ],
            metadata=dict(run.get("metadata", {})),
        )
        for run in raw.get("runs", [])
    ]
    return TraceBenchmark(
        benchmark_id=str(raw["benchmark_id"]),
        description=str(raw.get("description", "")),
        runs=runs,
    )


def load_config(path: str | Path) -> AuditConfig:
    return AuditConfig.from_dict(_load_json(path))


def write_experiment_result(path: str | Path, result: ExperimentResult) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(result), indent=2) + "\n", encoding="utf-8")
