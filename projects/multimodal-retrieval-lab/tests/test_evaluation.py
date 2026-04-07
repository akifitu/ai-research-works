from __future__ import annotations

import unittest
from pathlib import Path

from multimodal_retrieval_lab.dataset import load_benchmark, load_config
from multimodal_retrieval_lab.evaluation import evaluate_system


class EvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        benchmark = load_benchmark(project_root / "benchmarks" / "sample_multimodal_benchmark.json")
        self.config = load_config(project_root / "configs" / "default_retrieval_eval.json")
        self.scenario = benchmark.scenarios[0]

    def test_fusion_system_beats_caption_drift(self) -> None:
        systems = {
            system.system_id: system for system in self.scenario.systems
        }
        fusion = evaluate_system(systems["fusion_reranker"], self.scenario, self.config)
        drift = evaluate_system(systems["caption_drift_model"], self.scenario, self.config)

        self.assertGreater(fusion.overall_score, drift.overall_score)
        self.assertGreater(fusion.recall_at_k, drift.recall_at_k)
        self.assertLess(fusion.hard_negative_rate, drift.hard_negative_rate)


if __name__ == "__main__":
    unittest.main()
