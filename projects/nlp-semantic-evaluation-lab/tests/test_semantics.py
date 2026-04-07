from __future__ import annotations

import unittest

from nlp_semantic_evaluation_lab.semantics import entity_f1, lcs_similarity, token_overlap


class SemanticMetricTests(unittest.TestCase):
    def test_token_overlap_scores_shared_terms(self) -> None:
        score = token_overlap("late delivery refund", "refund after late delivery")

        self.assertGreater(score, 0.5)

    def test_lcs_similarity_preserves_order_signal(self) -> None:
        score = lcs_similarity("a b c d", "a c d")

        self.assertEqual(0.75, score)

    def test_entity_f1_normalizes_case_and_punctuation(self) -> None:
        precision, recall, f1 = entity_f1(["Billing Team", "invoice"], ["billing team", "outage"])

        self.assertEqual(0.5, precision)
        self.assertEqual(0.5, recall)
        self.assertEqual(0.5, f1)


if __name__ == "__main__":
    unittest.main()
