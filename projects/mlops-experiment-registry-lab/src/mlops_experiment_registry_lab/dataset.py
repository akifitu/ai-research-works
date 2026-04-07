from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ExperimentRun, RegistryBenchmark, RegistryPolicy


def _load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_policy(path: str | Path) -> RegistryPolicy:
    return RegistryPolicy.from_dict(_load_json(path))


def load_benchmark(path: str | Path) -> RegistryBenchmark:
    raw = _load_json(path)
    runs = [
        ExperimentRun(
            run_id=str(run["run_id"]),
            model_name=str(run["model_name"]),
            metrics={key: float(value) for key, value in run.get("metrics", {}).items()},
            parameters=dict(run.get("parameters", {})),
            metadata=dict(run.get("metadata", {})),
            tags=[str(tag) for tag in run.get("tags", [])],
        )
        for run in raw.get("runs", [])
    ]
    return RegistryBenchmark(
        benchmark_id=str(raw["benchmark_id"]),
        description=str(raw.get("description", "")),
        incumbent_run_id=raw.get("incumbent_run_id"),
        runs=runs,
    )
