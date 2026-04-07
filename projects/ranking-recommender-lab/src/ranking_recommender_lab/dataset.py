from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import (
    CatalogItem,
    ExperimentResult,
    RankingBenchmark,
    RankingEvalConfig,
    RankingQuery,
    RankingScenario,
    RankingSystem,
    RelevanceJudgment,
)


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_benchmark(path: str | Path) -> RankingBenchmark:
    raw = _load_json(path)
    scenarios = [
        RankingScenario(
            scenario_id=str(scenario["scenario_id"]),
            name=str(scenario["name"]),
            k=int(scenario.get("k", 5)),
            baseline_system_id=str(scenario["baseline_system_id"]),
            catalog=[
                CatalogItem(
                    item_id=str(item["item_id"]),
                    is_long_tail=bool(item["is_long_tail"]),
                    metadata=dict(item.get("metadata", {})),
                )
                for item in scenario.get("catalog", [])
            ],
            systems=[
                RankingSystem(
                    system_id=str(system["system_id"]),
                    family=str(system["family"]),
                    notes=str(system.get("notes", "")),
                    metadata=dict(system.get("metadata", {})),
                )
                for system in scenario.get("systems", [])
            ],
            queries=[
                RankingQuery(
                    query_id=str(query["query_id"]),
                    segment=str(query["segment"]),
                    relevant_items=[
                        RelevanceJudgment(
                            item_id=str(judgment["item_id"]),
                            grade=int(judgment["grade"]),
                        )
                        for judgment in query.get("relevant_items", [])
                    ],
                    predictions={
                        str(system_id): [str(item_id) for item_id in items]
                        for system_id, items in query.get("predictions", {}).items()
                    },
                    metadata=dict(query.get("metadata", {})),
                )
                for query in scenario.get("queries", [])
            ],
            metadata=dict(scenario.get("metadata", {})),
        )
        for scenario in raw.get("scenarios", [])
    ]
    return RankingBenchmark(
        benchmark_id=str(raw["benchmark_id"]),
        description=str(raw.get("description", "")),
        scenarios=scenarios,
    )


def load_config(path: str | Path) -> RankingEvalConfig:
    return RankingEvalConfig.from_dict(_load_json(path))


def write_experiment_result(path: str | Path, result: ExperimentResult) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(result), indent=2) + "\n", encoding="utf-8")
