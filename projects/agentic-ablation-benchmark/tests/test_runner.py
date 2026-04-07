from __future__ import annotations

import unittest
from pathlib import Path

from agentic_ablation_benchmark.dataset import load_benchmark, load_config
from agentic_ablation_benchmark.runner import ExperimentRunner


class RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        self.benchmark = load_benchmark(project_root / "benchmarks" / "sample_ablation_benchmark.json")
        self.config = load_config(project_root / "configs" / "default_ablation.json")

    def test_runner_emits_expected_findings(self) -> None:
        result = ExperimentRunner(self.config).run_benchmark(self.benchmark)
        findings = {
            finding.category
            for task_result in result.tasks
            for finding in task_result.findings
        }

        self.assertEqual("mini-agentic-ablation", result.benchmark_id)
        self.assertEqual(2, len(result.tasks))
        self.assertIn("WINNER", findings)
        self.assertIn("REGRESSION", findings)
        self.assertIn("LOOP_RISK", findings)
        self.assertIn("RECOVERY_GAP", findings)

    def test_aggregate_metrics_cover_all_variants(self) -> None:
        result = ExperimentRunner(self.config).run_benchmark(self.benchmark)

        self.assertEqual(2, result.aggregate_metrics.task_count)
        self.assertEqual(6, result.aggregate_metrics.variant_count)
        self.assertGreater(result.aggregate_metrics.mean_score, 0.0)
        self.assertGreater(result.aggregate_metrics.total_findings, 0)


if __name__ == "__main__":
    unittest.main()

