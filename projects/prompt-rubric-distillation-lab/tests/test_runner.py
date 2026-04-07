from __future__ import annotations

import unittest
from pathlib import Path

from prompt_rubric_distillation_lab.dataset import load_benchmark, load_config
from prompt_rubric_distillation_lab.runner import ExperimentRunner


class RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        self.benchmark = load_benchmark(project_root / "benchmarks" / "sample_rubrics.json")
        self.config = load_config(project_root / "configs" / "default_distillation.json")

    def test_runner_emits_rubric_findings_and_weights(self) -> None:
        result = ExperimentRunner(self.config).run_benchmark(self.benchmark)
        findings = {finding.category for rubric in result.rubrics for finding in rubric.findings}

        self.assertEqual("mini-rubric-distillation", result.benchmark_id)
        self.assertEqual(2, len(result.rubrics))
        self.assertIn("AMBIGUITY", findings)
        self.assertIn("WEIGHT_GAP", findings)

        for rubric in result.rubrics:
            total_weight = sum(item.normalized_weight for item in rubric.distilled_criteria)
            self.assertAlmostEqual(1.0, total_weight, places=3)

    def test_aggregate_metrics_reflect_all_criteria(self) -> None:
        result = ExperimentRunner(self.config).run_benchmark(self.benchmark)

        self.assertEqual(6, result.aggregate_metrics.total_criteria)
        self.assertGreater(result.aggregate_metrics.mean_ambiguity_rate, 0.0)
        self.assertGreater(result.aggregate_metrics.mean_specificity_score, 0.0)
        self.assertGreater(result.aggregate_metrics.total_findings, 0)


if __name__ == "__main__":
    unittest.main()
