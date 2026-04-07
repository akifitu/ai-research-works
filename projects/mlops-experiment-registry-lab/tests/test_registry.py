from __future__ import annotations

import unittest

from mlops_experiment_registry_lab.models import ExperimentRun, RegistryPolicy
from mlops_experiment_registry_lab.registry import rank_runs, validate_run


class RegistryPolicyTests(unittest.TestCase):
    def test_rank_runs_uses_metric_mode(self) -> None:
        policy = RegistryPolicy(metric_name="loss", mode="min")
        runs = [
            ExperimentRun("slow", "model-a", {"loss": 0.4}, metadata={"dataset_id": "d", "code_sha": "a", "created_at": "t"}),
            ExperimentRun("best", "model-b", {"loss": 0.2}, metadata={"dataset_id": "d", "code_sha": "b", "created_at": "t"}),
        ]

        ranked = rank_runs(runs, policy)

        self.assertEqual("best", ranked[0].run_id)

    def test_validate_run_flags_blocked_tags(self) -> None:
        policy = RegistryPolicy(blocked_tags=["unsafe"])
        run = ExperimentRun(
            "candidate",
            "model",
            {"eval_f1": 0.9},
            metadata={"dataset_id": "d", "code_sha": "s", "created_at": "t"},
            tags=["unsafe"],
        )

        self.assertEqual(["blocked tags: unsafe"], validate_run(run, policy))


if __name__ == "__main__":
    unittest.main()
