from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import (
    AssetCard,
    ExperimentResult,
    RetrievalBenchmark,
    RetrievalEvalConfig,
    RetrievalQuery,
    RetrievalScenario,
    RetrievalSystem,
)


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_benchmark(path: str | Path) -> RetrievalBenchmark:
    raw = _load_json(path)
    scenarios = [
        RetrievalScenario(
            scenario_id=str(scenario["scenario_id"]),
            name=str(scenario["name"]),
            k=int(scenario.get("k", 3)),
            baseline_system_id=str(scenario["baseline_system_id"]),
            assets=[
                AssetCard(
                    asset_id=str(asset["asset_id"]),
                    modality=str(asset["modality"]),
                    metadata=dict(asset.get("metadata", {})),
                )
                for asset in scenario.get("assets", [])
            ],
            systems=[
                RetrievalSystem(
                    system_id=str(system["system_id"]),
                    family=str(system["family"]),
                    notes=str(system.get("notes", "")),
                    metadata=dict(system.get("metadata", {})),
                )
                for system in scenario.get("systems", [])
            ],
            queries=[
                RetrievalQuery(
                    query_id=str(query["query_id"]),
                    direction=str(query["direction"]),
                    segment=str(query["segment"]),
                    relevant_target_ids=[
                        str(target_id) for target_id in query.get("relevant_target_ids", [])
                    ],
                    hard_negative_ids=[
                        str(target_id) for target_id in query.get("hard_negative_ids", [])
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
    return RetrievalBenchmark(
        benchmark_id=str(raw["benchmark_id"]),
        description=str(raw.get("description", "")),
        scenarios=scenarios,
    )


def load_config(path: str | Path) -> RetrievalEvalConfig:
    return RetrievalEvalConfig.from_dict(_load_json(path))


def write_experiment_result(path: str | Path, result: ExperimentResult) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(result), indent=2) + "\n", encoding="utf-8")
