from __future__ import annotations

import unittest
from pathlib import Path

from bandit_policy_evaluation_lab.dataset import load_benchmark, load_config
from bandit_policy_evaluation_lab.evaluation import evaluate_policy


class EvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        benchmark = load_benchmark(project_root / "benchmarks" / "sample_bandit_benchmark.json")
        self.config = load_config(project_root / "configs" / "default_policy_eval.json")
        self.homepage_scenario = benchmark.scenarios[0]

    def test_greedy_candidate_beats_unstable_explorer(self) -> None:
        policies = {
            policy.policy_id: policy for policy in self.homepage_scenario.policies
        }
        greedy = evaluate_policy(
            policies["greedy_personalized"],
            self.homepage_scenario.events,
            self.config,
        )
        explorer = evaluate_policy(
            policies["broad_explorer"],
            self.homepage_scenario.events,
            self.config,
        )

        self.assertGreater(greedy.overall_score, explorer.overall_score)
        self.assertLess(explorer.effective_sample_ratio, self.config.min_effective_sample_ratio)
        self.assertLess(greedy.support_rate, 1.0)


if __name__ == "__main__":
    unittest.main()
