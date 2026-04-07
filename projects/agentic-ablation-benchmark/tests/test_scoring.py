from __future__ import annotations

import unittest

from agentic_ablation_benchmark.models import AblationConfig, VariantRun
from agentic_ablation_benchmark.scoring import changed_factors, score_variant


class ScoringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = AblationConfig(
            latency_budget_ms=5000,
            token_budget=1300,
            ideal_tool_calls=6,
            regression_threshold=0.08,
            loop_penalty=0.08,
        )

    def test_scores_efficient_completed_variant_higher(self) -> None:
        strong = VariantRun(
            variant_id="strong",
            prompt_strategy="structured",
            tool_policy="default",
            retrieval_policy="none",
            completed=True,
            quality_score=0.86,
            tool_calls=5,
            failed_calls=1,
            recovered_failures=1,
            loop_events=0,
            latency_ms=3600,
            prompt_tokens=760,
            completion_tokens=330,
        )
        weak = VariantRun(
            variant_id="weak",
            prompt_strategy="default",
            tool_policy="aggressive",
            retrieval_policy="none",
            completed=True,
            quality_score=0.72,
            tool_calls=10,
            failed_calls=2,
            recovered_failures=1,
            loop_events=2,
            latency_ms=6200,
            prompt_tokens=880,
            completion_tokens=420,
        )

        self.assertGreater(score_variant(strong, self.config).overall_score, score_variant(weak, self.config).overall_score)

    def test_changed_factors_detects_policy_differences(self) -> None:
        baseline = VariantRun(
            variant_id="baseline",
            prompt_strategy="default",
            tool_policy="default",
            retrieval_policy="light",
            completed=True,
            quality_score=0.7,
            tool_calls=6,
            failed_calls=0,
            recovered_failures=0,
            loop_events=0,
            latency_ms=4000,
            prompt_tokens=600,
            completion_tokens=300,
        )
        candidate = VariantRun(
            variant_id="candidate",
            prompt_strategy="structured",
            tool_policy="default",
            retrieval_policy="deep",
            completed=True,
            quality_score=0.75,
            tool_calls=6,
            failed_calls=0,
            recovered_failures=0,
            loop_events=0,
            latency_ms=4100,
            prompt_tokens=650,
            completion_tokens=320,
        )

        self.assertEqual(
            ["prompt:structured", "retrieval:deep"],
            changed_factors(baseline, candidate),
        )


if __name__ == "__main__":
    unittest.main()

