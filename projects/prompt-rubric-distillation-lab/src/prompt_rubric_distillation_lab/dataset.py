from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import (
    DistillationConfig,
    ExperimentResult,
    Rubric,
    RubricBenchmark,
    RubricCriterion,
)


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_benchmark(path: str | Path) -> RubricBenchmark:
    raw = _load_json(path)
    rubrics = [
        Rubric(
            rubric_id=str(rubric["rubric_id"]),
            task=str(rubric["task"]),
            criteria=[
                RubricCriterion(
                    criterion_id=str(criterion["criterion_id"]),
                    text=str(criterion["text"]),
                    weight=(
                        float(criterion["weight"])
                        if criterion.get("weight") is not None
                        else None
                    ),
                    metadata=dict(criterion.get("metadata", {})),
                )
                for criterion in rubric.get("criteria", [])
            ],
            metadata=dict(rubric.get("metadata", {})),
        )
        for rubric in raw.get("rubrics", [])
    ]
    return RubricBenchmark(
        benchmark_id=str(raw["benchmark_id"]),
        description=str(raw.get("description", "")),
        rubrics=rubrics,
    )


def load_config(path: str | Path) -> DistillationConfig:
    return DistillationConfig.from_dict(_load_json(path))


def write_experiment_result(path: str | Path, result: ExperimentResult) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(result), indent=2) + "\n", encoding="utf-8")
