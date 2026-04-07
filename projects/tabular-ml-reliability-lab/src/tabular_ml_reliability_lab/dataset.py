from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ReliabilityConfig, TabularBenchmark


def _load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_config(path: str | Path) -> ReliabilityConfig:
    return ReliabilityConfig.from_dict(_load_json(path))


def load_benchmark(path: str | Path) -> TabularBenchmark:
    raw = _load_json(path)
    return TabularBenchmark(
        benchmark_id=str(raw["benchmark_id"]),
        description=str(raw.get("description", "")),
        baseline_rows=[dict(row) for row in raw.get("baseline_rows", [])],
        current_rows=[dict(row) for row in raw.get("current_rows", [])],
    )
