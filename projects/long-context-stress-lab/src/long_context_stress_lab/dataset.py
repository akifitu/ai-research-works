from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import (
    AnswerSnapshot,
    ContextItem,
    ExperimentResult,
    StressBenchmark,
    StressCase,
    StressConfig,
)


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_benchmark(path: str | Path) -> StressBenchmark:
    raw = _load_json(path)
    cases = [
        StressCase(
            case_id=str(case["case_id"]),
            question=str(case["question"]),
            reference_answer=str(case["reference_answer"]),
            context_items=[
                ContextItem(
                    item_id=str(item["item_id"]),
                    title=str(item["title"]),
                    text=str(item["text"]),
                    estimated_tokens=int(item["estimated_tokens"]),
                    priority=int(item.get("priority", 0)),
                    relevance=bool(item.get("relevance", False)),
                    metadata=dict(item.get("metadata", {})),
                )
                for item in case.get("context_items", [])
            ],
            answer_snapshots=[
                AnswerSnapshot(
                    snapshot_id=str(snapshot["snapshot_id"]),
                    budget_tokens=int(snapshot["budget_tokens"]),
                    answer=str(snapshot["answer"]),
                    metadata=dict(snapshot.get("metadata", {})),
                )
                for snapshot in case.get("answer_snapshots", [])
            ],
            metadata=dict(case.get("metadata", {})),
        )
        for case in raw.get("cases", [])
    ]
    return StressBenchmark(
        benchmark_id=str(raw["benchmark_id"]),
        description=str(raw.get("description", "")),
        cases=cases,
    )


def load_config(path: str | Path) -> StressConfig:
    return StressConfig.from_dict(_load_json(path))


def write_experiment_result(path: str | Path, result: ExperimentResult) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(result), indent=2) + "\n", encoding="utf-8")
