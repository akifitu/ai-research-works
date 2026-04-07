from __future__ import annotations

import unittest
from pathlib import Path

from tool_trajectory_audit_lab.dataset import load_benchmark, load_config
from tool_trajectory_audit_lab.runner import ExperimentRunner


class TraceRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        self.benchmark = load_benchmark(project_root / "benchmarks" / "sample_traces.json")
        self.config = load_config(project_root / "configs" / "default_audit.json")

    def test_runner_builds_aggregate_benchmark_result(self) -> None:
        result = ExperimentRunner(self.config).run_benchmark(self.benchmark)

        self.assertEqual("mini-tool-trace-audit", result.benchmark_id)
        self.assertEqual(2, len(result.runs))
        self.assertEqual(3, result.aggregate_metrics.total_failures)
        self.assertGreater(result.aggregate_metrics.total_loops, 0)
        self.assertGreater(result.aggregate_metrics.mean_efficiency_score, 0.0)


if __name__ == "__main__":
    unittest.main()
