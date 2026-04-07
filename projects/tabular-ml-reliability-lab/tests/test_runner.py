from __future__ import annotations

import unittest
from pathlib import Path

from tabular_ml_reliability_lab.dataset import load_benchmark, load_config
from tabular_ml_reliability_lab.runner import TabularReliabilityRunner


class TabularRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        self.benchmark = load_benchmark(project_root / "benchmarks" / "sample_tabular_benchmark.json")
        self.config = load_config(project_root / "configs" / "default_reliability.json")

    def test_runner_flags_income_drift(self) -> None:
        result = TabularReliabilityRunner(self.config).run_benchmark(self.benchmark)
        findings = {finding.feature: finding for finding in result.drift_findings}

        self.assertEqual("HIGH", findings["income"].risk_level)
        self.assertIn("approved_copy", result.leakage_candidates)
        self.assertGreater(result.high_risk_feature_count, 0)

    def test_runner_flags_region_coverage_shift(self) -> None:
        result = TabularReliabilityRunner(self.config).run_benchmark(self.benchmark)
        findings = {finding.feature: finding for finding in result.drift_findings}

        self.assertEqual("HIGH", findings["region"].risk_level)


if __name__ == "__main__":
    unittest.main()
