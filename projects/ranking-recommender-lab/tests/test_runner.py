from __future__ import annotations

import unittest
from pathlib import Path

from ranking_recommender_lab.dataset import load_benchmark, load_config
from ranking_recommender_lab.runner import ExperimentRunner


class RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        self.benchmark = load_benchmark(project_root / "benchmarks" / "sample_ranking_benchmark.json")
        self.config = load_config(project_root / "configs" / "default_ranking_eval.json")

    def test_runner_emits_expected_findings(self) -> None:
        result = ExperimentRunner(self.config).run_benchmark(self.benchmark)
        findings = {
            finding.category
            for scenario_result in result.scenarios
            for finding in scenario_result.findings
        }

        self.assertEqual("mini-ranking-recommender-benchmark", result.benchmark_id)
        self.assertEqual(2, len(result.scenarios))
        self.assertIn("WINNER", findings)
        self.assertIn("BASELINE_REGRESSION", findings)
        self.assertIn("COLD_START_GAP", findings)
        self.assertIn("COVERAGE_RISK", findings)
        self.assertIn("POPULARITY_BIAS", findings)

    def test_aggregate_metrics_cover_all_systems(self) -> None:
        result = ExperimentRunner(self.config).run_benchmark(self.benchmark)

        self.assertEqual(2, result.aggregate_metrics.scenario_count)
        self.assertEqual(6, result.aggregate_metrics.system_count)
        self.assertGreater(result.aggregate_metrics.total_findings, 0)
        self.assertGreater(result.aggregate_metrics.mean_ndcg_at_k, 0.0)


if __name__ == "__main__":
    unittest.main()
