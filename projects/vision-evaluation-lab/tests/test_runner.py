from __future__ import annotations

import unittest
from pathlib import Path

from vision_evaluation_lab.dataset import load_benchmark, load_config
from vision_evaluation_lab.runner import VisionEvaluationRunner


class VisionRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        self.benchmark = load_benchmark(project_root / "benchmarks" / "sample_vision_benchmark.json")
        self.config = load_config(project_root / "configs" / "default_vision_eval.json")

    def test_runner_evaluates_all_samples(self) -> None:
        result = VisionEvaluationRunner(self.config).run_benchmark(self.benchmark)

        self.assertEqual("mini-vision-eval", result.benchmark_id)
        self.assertEqual(3, len(result.samples))
        self.assertGreater(result.detection_precision, 0.0)
        self.assertLess(result.detection_recall, 1.0)

    def test_classification_metrics_include_error_class(self) -> None:
        result = VisionEvaluationRunner(self.config).run_benchmark(self.benchmark)
        by_label = {metric.label: metric for metric in result.classification_metrics}

        self.assertEqual(1, by_label["cyclist"].false_positive)
        self.assertEqual(1, by_label["pedestrian"].false_negative)


if __name__ == "__main__":
    unittest.main()
