from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import Benchmark, BenchmarkSample, Document, ExperimentConfig, ExperimentResult


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_benchmark(path: str | Path) -> Benchmark:
    raw = _load_json(path)
    samples = [
        BenchmarkSample(
            sample_id=str(sample["sample_id"]),
            question=str(sample["question"]),
            answer=str(sample["answer"]),
            documents=[
                Document(
                    doc_id=str(document["doc_id"]),
                    title=str(document["title"]),
                    text=str(document["text"]),
                    metadata=dict(document.get("metadata", {})),
                )
                for document in sample.get("documents", [])
            ],
            metadata=dict(sample.get("metadata", {})),
        )
        for sample in raw.get("samples", [])
    ]
    return Benchmark(
        benchmark_id=str(raw["benchmark_id"]),
        description=str(raw.get("description", "")),
        samples=samples,
    )


def load_config(path: str | Path) -> ExperimentConfig:
    return ExperimentConfig.from_dict(_load_json(path))


def write_experiment_result(path: str | Path, result: ExperimentResult) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(result), indent=2) + "\n", encoding="utf-8")
