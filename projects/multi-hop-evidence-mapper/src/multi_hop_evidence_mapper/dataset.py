from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import (
    Document,
    ExperimentResult,
    MappingConfig,
    MultiHopBenchmark,
    MultiHopCase,
    ReasoningHop,
)


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_benchmark(path: str | Path) -> MultiHopBenchmark:
    raw = _load_json(path)
    cases = [
        MultiHopCase(
            case_id=str(case["case_id"]),
            question=str(case["question"]),
            answer=str(case["answer"]),
            documents=[
                Document(
                    doc_id=str(document["doc_id"]),
                    title=str(document["title"]),
                    text=str(document["text"]),
                    metadata=dict(document.get("metadata", {})),
                )
                for document in case.get("documents", [])
            ],
            reasoning_hops=[
                ReasoningHop(
                    hop_id=str(hop["hop_id"]),
                    claim=str(hop["claim"]),
                    bridge_terms=[str(term) for term in hop.get("bridge_terms", [])],
                    metadata=dict(hop.get("metadata", {})),
                )
                for hop in case.get("reasoning_hops", [])
            ],
            conclusion_claim=str(case["conclusion_claim"]),
            metadata=dict(case.get("metadata", {})),
        )
        for case in raw.get("cases", [])
    ]
    return MultiHopBenchmark(
        benchmark_id=str(raw["benchmark_id"]),
        description=str(raw.get("description", "")),
        cases=cases,
    )


def load_config(path: str | Path) -> MappingConfig:
    return MappingConfig.from_dict(_load_json(path))


def write_experiment_result(path: str | Path, result: ExperimentResult) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(result), indent=2) + "\n", encoding="utf-8")
