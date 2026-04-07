from __future__ import annotations

import unittest
from pathlib import Path

from citation_grounding_lab.claims import extract_claims
from citation_grounding_lab.dataset import load_benchmark


class ClaimExtractionTests(unittest.TestCase):
    def setUp(self) -> None:
        benchmark_path = Path(__file__).resolve().parents[1] / "benchmarks" / "sample_benchmark.json"
        self.benchmark = load_benchmark(benchmark_path)

    def test_extracts_multiple_claims_from_multi_sentence_answer(self) -> None:
        sample = self.benchmark.samples[0]
        claims = extract_claims(sample)

        self.assertEqual(2, len(claims))
        self.assertEqual(["doc_transformer_core"], claims[0].cited_doc_ids)
        self.assertIn("self-attention allows tokens to be processed in parallel", claims[0].text)

    def test_preserves_citation_ids_per_sentence(self) -> None:
        sample = self.benchmark.samples[1]
        claims = extract_claims(sample)

        self.assertEqual(["doc_rag_failures"], claims[0].cited_doc_ids)
        self.assertEqual(["doc_rag_failures"], claims[1].cited_doc_ids)


if __name__ == "__main__":
    unittest.main()
