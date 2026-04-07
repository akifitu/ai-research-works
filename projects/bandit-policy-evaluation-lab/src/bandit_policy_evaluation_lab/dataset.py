from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import (
    BanditBenchmark,
    ExperimentResult,
    LoggedEvent,
    PolicyCard,
    PolicyEvalConfig,
    Scenario,
)


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_benchmark(path: str | Path) -> BanditBenchmark:
    raw = _load_json(path)
    scenarios = [
        Scenario(
            scenario_id=str(scenario["scenario_id"]),
            name=str(scenario["name"]),
            baseline_policy_id=str(scenario["baseline_policy_id"]),
            policies=[
                PolicyCard(
                    policy_id=str(policy["policy_id"]),
                    family=str(policy["family"]),
                    exploration_rate=float(policy["exploration_rate"]),
                    notes=str(policy.get("notes", "")),
                    metadata=dict(policy.get("metadata", {})),
                )
                for policy in scenario.get("policies", [])
            ],
            events=[
                LoggedEvent(
                    event_id=str(event["event_id"]),
                    action_taken=str(event["action_taken"]),
                    reward=float(event["reward"]),
                    oracle_reward=float(event["oracle_reward"]),
                    logging_propensity=float(event["logging_propensity"]),
                    segment=str(event["segment"]),
                    policy_support={
                        str(policy_id): float(propensity)
                        for policy_id, propensity in event.get("policy_support", {}).items()
                    },
                    metadata=dict(event.get("metadata", {})),
                )
                for event in scenario.get("events", [])
            ],
            metadata=dict(scenario.get("metadata", {})),
        )
        for scenario in raw.get("scenarios", [])
    ]
    return BanditBenchmark(
        benchmark_id=str(raw["benchmark_id"]),
        description=str(raw.get("description", "")),
        scenarios=scenarios,
    )


def load_config(path: str | Path) -> PolicyEvalConfig:
    return PolicyEvalConfig.from_dict(_load_json(path))


def write_experiment_result(path: str | Path, result: ExperimentResult) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(result), indent=2) + "\n", encoding="utf-8")
