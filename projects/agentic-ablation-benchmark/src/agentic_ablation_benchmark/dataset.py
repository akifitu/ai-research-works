from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import AblationBenchmark, AblationConfig, BenchmarkTask, ExperimentResult, VariantRun


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_benchmark(path: str | Path) -> AblationBenchmark:
    raw = _load_json(path)
    tasks = [
        BenchmarkTask(
            task_id=str(task["task_id"]),
            name=str(task["name"]),
            baseline_variant_id=str(task["baseline_variant_id"]),
            variants=[
                VariantRun(
                    variant_id=str(variant["variant_id"]),
                    prompt_strategy=str(variant["prompt_strategy"]),
                    tool_policy=str(variant["tool_policy"]),
                    retrieval_policy=str(variant["retrieval_policy"]),
                    completed=bool(variant["completed"]),
                    quality_score=float(variant["quality_score"]),
                    tool_calls=int(variant["tool_calls"]),
                    failed_calls=int(variant["failed_calls"]),
                    recovered_failures=int(variant["recovered_failures"]),
                    loop_events=int(variant["loop_events"]),
                    latency_ms=int(variant["latency_ms"]),
                    prompt_tokens=int(variant["prompt_tokens"]),
                    completion_tokens=int(variant["completion_tokens"]),
                    metadata=dict(variant.get("metadata", {})),
                )
                for variant in task.get("variants", [])
            ],
            metadata=dict(task.get("metadata", {})),
        )
        for task in raw.get("tasks", [])
    ]
    return AblationBenchmark(
        benchmark_id=str(raw["benchmark_id"]),
        description=str(raw.get("description", "")),
        tasks=tasks,
    )


def load_config(path: str | Path) -> AblationConfig:
    return AblationConfig.from_dict(_load_json(path))


def write_experiment_result(path: str | Path, result: ExperimentResult) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(result), indent=2) + "\n", encoding="utf-8")

