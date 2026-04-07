from __future__ import annotations

import unittest
from pathlib import Path

from long_context_stress_lab.dataset import load_benchmark, load_config
from long_context_stress_lab.runner import ExperimentRunner


class RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        self.benchmark = load_benchmark(project_root / "benchmarks" / "sample_context_benchmark.json")
        self.config = load_config(project_root / "configs" / "default_stress.json")

    def test_benchmark_emits_expected_findings(self) -> None:
        result = ExperimentRunner(self.config).run_benchmark(self.benchmark)
        findings = {
            finding.category
            for case_result in result.cases
            for evaluation in case_result.evaluations
            for finding in evaluation.findings
        }

        self.assertEqual("mini-long-context-stress", result.benchmark_id)
        self.assertEqual(2, len(result.cases))
        self.assertIn("OVERFLOW", findings)
        self.assertIn("DRIFT", findings)
        self.assertIn("DILUTION", findings)
        self.assertIn("UNSUPPORTED_INSERTION", findings)

    def test_aggregate_metrics_cover_all_snapshots(self) -> None:
        result = ExperimentRunner(self.config).run_benchmark(self.benchmark)

        self.assertEqual(5, result.aggregate_metrics.snapshot_count)
        self.assertGreater(result.aggregate_metrics.mean_relevant_coverage, 0.0)
        self.assertGreater(result.aggregate_metrics.max_drift_score, 0.0)
        self.assertGreater(result.aggregate_metrics.total_findings, 0)


if __name__ == "__main__":
    unittest.main()
