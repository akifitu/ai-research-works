from __future__ import annotations

import unittest
from pathlib import Path

from ranking_recommender_lab.dataset import load_benchmark, load_config
from ranking_recommender_lab.evaluation import evaluate_system


class EvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        benchmark = load_benchmark(project_root / "benchmarks" / "sample_ranking_benchmark.json")
        self.config = load_config(project_root / "configs" / "default_ranking_eval.json")
        self.homepage_scenario = benchmark.scenarios[0]

    def test_hybrid_beats_trend_hunter(self) -> None:
        systems = {
            system.system_id: system for system in self.homepage_scenario.systems
        }
        hybrid = evaluate_system(
            systems["hybrid_personalized"],
            self.homepage_scenario,
            self.config,
        )
        trend = evaluate_system(
            systems["trend_hunter"],
            self.homepage_scenario,
            self.config,
        )

        self.assertGreater(hybrid.overall_score, trend.overall_score)
        self.assertGreater(hybrid.ndcg_at_k, trend.ndcg_at_k)
        self.assertGreater(hybrid.long_tail_share, trend.long_tail_share)


if __name__ == "__main__":
    unittest.main()
