from __future__ import annotations

import unittest
from pathlib import Path

from bandit_policy_evaluation_lab.dataset import load_benchmark, load_config
from bandit_policy_evaluation_lab.runner import ExperimentRunner


class RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        self.benchmark = load_benchmark(project_root / "benchmarks" / "sample_bandit_benchmark.json")
        self.config = load_config(project_root / "configs" / "default_policy_eval.json")

    def test_runner_emits_expected_findings(self) -> None:
        result = ExperimentRunner(self.config).run_benchmark(self.benchmark)
        findings = {
            finding.category
            for scenario_result in result.scenarios
            for finding in scenario_result.findings
        }

        self.assertEqual("mini-bandit-policy-benchmark", result.benchmark_id)
        self.assertEqual(2, len(result.scenarios))
        self.assertIn("WINNER", findings)
        self.assertIn("REGRET_ALERT", findings)
        self.assertIn("SUPPORT_GAP", findings)
        self.assertIn("VARIANCE_RISK", findings)
        self.assertIn("SEGMENT_DROP", findings)
        self.assertIn("BASELINE_REGRESSION", findings)

    def test_aggregate_metrics_cover_all_policies(self) -> None:
        result = ExperimentRunner(self.config).run_benchmark(self.benchmark)

        self.assertEqual(2, result.aggregate_metrics.scenario_count)
        self.assertEqual(6, result.aggregate_metrics.policy_count)
        self.assertGreater(result.aggregate_metrics.total_findings, 0)
        self.assertGreater(result.aggregate_metrics.mean_snips_reward, 0.0)


if __name__ == "__main__":
    unittest.main()
