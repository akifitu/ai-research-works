from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ForecastConfig, TimeSeriesBenchmark, TimeSeriesSample


def _load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_config(path: str | Path) -> ForecastConfig:
    return ForecastConfig.from_dict(_load_json(path))


def load_benchmark(path: str | Path) -> TimeSeriesBenchmark:
    raw = _load_json(path)
    return TimeSeriesBenchmark(
        benchmark_id=str(raw["benchmark_id"]),
        description=str(raw.get("description", "")),
        series=[
            TimeSeriesSample(
                series_id=str(sample["series_id"]),
                values=[float(value) for value in sample.get("values", [])],
                metadata=dict(sample.get("metadata", {})),
            )
            for sample in raw.get("series", [])
        ],
    )
