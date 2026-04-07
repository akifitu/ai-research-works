from __future__ import annotations

import unittest
from pathlib import Path

from nlp_semantic_evaluation_lab.dataset import load_benchmark, load_config
from nlp_semantic_evaluation_lab.runner import NlpSemanticEvaluationRunner


class NlpRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        self.benchmark = load_benchmark(project_root / "benchmarks" / "sample_nlp_benchmark.json")
        self.config = load_config(project_root / "configs" / "default_nlp_eval.json")

    def test_runner_builds_corpus_metrics(self) -> None:
        result = NlpSemanticEvaluationRunner(self.config).run_benchmark(self.benchmark)

        self.assertEqual("mini-nlp-semantic-eval", result.benchmark_id)
        self.assertEqual(3, len(result.samples))
        self.assertGreater(result.mean_quality_score, 0.0)
        self.assertLess(result.intent_accuracy, 1.0)

    def test_last_sample_receives_low_entity_score(self) -> None:
        result = NlpSemanticEvaluationRunner(self.config).run_benchmark(self.benchmark)

        self.assertEqual(0.0, result.samples[-1].entity_f1)


if __name__ == "__main__":
    unittest.main()
