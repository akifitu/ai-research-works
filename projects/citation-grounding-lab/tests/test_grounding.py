from __future__ import annotations

import unittest
from pathlib import Path

from citation_grounding_lab.claims import extract_claims
from citation_grounding_lab.dataset import load_benchmark, load_config
from citation_grounding_lab.grounding import assess_claim
from citation_grounding_lab.models import CONTRADICTED, PARTIAL, SUPPORTED
from citation_grounding_lab.retrieval import LexicalRetriever, chunk_documents
from citation_grounding_lab.runner import ExperimentRunner


class GroundingPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        self.benchmark = load_benchmark(project_root / "benchmarks" / "sample_benchmark.json")
        self.config = load_config(project_root / "configs" / "default_experiment.json")

    def test_supported_claim_matches_cited_document(self) -> None:
        sample = self.benchmark.samples[1]
        claim = extract_claims(sample)[0]
        retriever = LexicalRetriever(
            chunk_documents(sample.documents, self.config.chunk_size, self.config.chunk_overlap)
        )

        assessment = assess_claim(claim, retriever.retrieve(claim.text, self.config.top_k), self.config)

        self.assertIn(assessment.label, {SUPPORTED, PARTIAL})
        self.assertIn("doc_rag_failures", assessment.matched_doc_ids)

    def test_negation_conflict_is_marked_as_contradicted(self) -> None:
        sample = self.benchmark.samples[2]
        claim = extract_claims(sample)[0]
        retriever = LexicalRetriever(
            chunk_documents(sample.documents, self.config.chunk_size, self.config.chunk_overlap)
        )

        assessment = assess_claim(claim, retriever.retrieve(claim.text, self.config.top_k), self.config)

        self.assertEqual(CONTRADICTED, assessment.label)

    def test_runner_builds_result_for_entire_benchmark(self) -> None:
        result = ExperimentRunner(self.config).run_benchmark(self.benchmark)

        self.assertEqual("mini-citation-grounding", result.benchmark_id)
        self.assertEqual(3, len(result.samples))
        self.assertGreaterEqual(result.aggregate_metrics.claim_count, 5)


if __name__ == "__main__":
    unittest.main()
