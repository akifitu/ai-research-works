from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import NlpBenchmark, NlpEvaluationConfig, NlpSample


def _load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_config(path: str | Path) -> NlpEvaluationConfig:
    return NlpEvaluationConfig.from_dict(_load_json(path))


def load_benchmark(path: str | Path) -> NlpBenchmark:
    raw = _load_json(path)
    samples = [
        NlpSample(
            sample_id=str(sample["sample_id"]),
            reference=str(sample["reference"]),
            prediction=str(sample["prediction"]),
            expected_entities=[str(entity) for entity in sample.get("expected_entities", [])],
            predicted_entities=[str(entity) for entity in sample.get("predicted_entities", [])],
            expected_intent=sample.get("expected_intent"),
            predicted_intent=sample.get("predicted_intent"),
            metadata=dict(sample.get("metadata", {})),
        )
        for sample in raw.get("samples", [])
    ]
    return NlpBenchmark(
        benchmark_id=str(raw["benchmark_id"]),
        description=str(raw.get("description", "")),
        samples=samples,
    )
