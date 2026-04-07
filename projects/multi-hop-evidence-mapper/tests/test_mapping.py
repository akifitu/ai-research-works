from __future__ import annotations

import unittest
from pathlib import Path

from multi_hop_evidence_mapper.dataset import load_benchmark
from multi_hop_evidence_mapper.mapping import evaluate_bridge_with_documents, map_hop_to_documents


class MappingTests(unittest.TestCase):
    def setUp(self) -> None:
        benchmark_path = (
            Path(__file__).resolve().parents[1]
            / "benchmarks"
            / "sample_multi_hop.json"
        )
        self.benchmark = load_benchmark(benchmark_path)

    def test_clean_chain_maps_first_hop_to_acquisition_doc(self) -> None:
        case = self.benchmark.cases[0]
        evaluation = map_hop_to_documents(case.reasoning_hops[0], case.documents)

        self.assertEqual("doc_acquisition", evaluation.doc_scores[0].doc_id)
        self.assertGreater(evaluation.support_score, 0.6)

    def test_broken_chain_bridge_support_is_weaker(self) -> None:
        clean_case = self.benchmark.cases[0]
        broken_case = self.benchmark.cases[1]

        clean_bridge = evaluate_bridge_with_documents(
            map_hop_to_documents(clean_case.reasoning_hops[0], clean_case.documents),
            map_hop_to_documents(clean_case.reasoning_hops[1], clean_case.documents),
            clean_case.documents,
        )
        broken_bridge = evaluate_bridge_with_documents(
            map_hop_to_documents(broken_case.reasoning_hops[0], broken_case.documents),
            map_hop_to_documents(broken_case.reasoning_hops[1], broken_case.documents),
            broken_case.documents,
        )

        self.assertGreater(clean_bridge.support_score, broken_bridge.support_score)


if __name__ == "__main__":
    unittest.main()
