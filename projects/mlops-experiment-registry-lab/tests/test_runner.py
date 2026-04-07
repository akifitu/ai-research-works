from __future__ import annotations

import unittest
from pathlib import Path

from mlops_experiment_registry_lab.dataset import load_benchmark, load_policy
from mlops_experiment_registry_lab.runner import ExperimentRegistryRunner


class RegistryRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        self.benchmark = load_benchmark(
            project_root / "benchmarks" / "sample_registry_benchmark.json"
        )
        self.policy = load_policy(project_root / "configs" / "default_registry_policy.json")

    def test_runner_promotes_safe_candidate_over_incumbent(self) -> None:
        result = ExperimentRegistryRunner(self.policy).run_benchmark(self.benchmark)

        self.assertEqual("mini-mlops-registry", result.benchmark_id)
        self.assertEqual("run-candidate-014", result.decision.candidate_run_id)
        self.assertTrue(result.decision.promoted)
        self.assertGreater(result.decision.metric_delta, self.policy.min_improvement)

    def test_blocked_high_metric_run_is_not_candidate(self) -> None:
        result = ExperimentRegistryRunner(self.policy).run_benchmark(self.benchmark)

        self.assertEqual("run-leaky-099", result.ranked_runs[0].run_id)
        self.assertEqual("run-candidate-014", result.decision.candidate_run_id)


if __name__ == "__main__":
    unittest.main()
