from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import BoundingBox, VisionBenchmark, VisionConfig, VisionSample


def _load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_config(path: str | Path) -> VisionConfig:
    return VisionConfig.from_dict(_load_json(path))


def load_benchmark(path: str | Path) -> VisionBenchmark:
    raw = _load_json(path)
    samples = []
    for sample in raw.get("samples", []):
        samples.append(
            VisionSample(
                image_id=str(sample["image_id"]),
                ground_truth_label=str(sample["ground_truth_label"]),
                predicted_label=str(sample["predicted_label"]),
                ground_truth_boxes=[
                    BoundingBox.from_dict(box) for box in sample.get("ground_truth_boxes", [])
                ],
                predicted_boxes=[
                    BoundingBox.from_dict(box) for box in sample.get("predicted_boxes", [])
                ],
                metadata=dict(sample.get("metadata", {})),
            )
        )
    return VisionBenchmark(
        benchmark_id=str(raw["benchmark_id"]),
        description=str(raw.get("description", "")),
        samples=samples,
    )
