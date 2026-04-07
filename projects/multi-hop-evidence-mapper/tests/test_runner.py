from __future__ import annotations

import unittest
from pathlib import Path

from multi_hop_evidence_mapper.dataset import load_benchmark, load_config
from multi_hop_evidence_mapper.runner import ExperimentRunner


class RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        self.benchmark = load_benchmark(project_root / "benchmarks" / "sample_multi_hop.json")
        self.config = load_config(project_root / "configs" / "default_mapping.json")

    def test_runner_emits_expected_chain_findings(self) -> None:
        result = ExperimentRunner(self.config).run_benchmark(self.benchmark)
        findings = {
            finding.category
            for case_result in result.cases
            for finding in case_result.findings
        }

        self.assertEqual("mini-multi-hop-mapper", result.benchmark_id)
        self.assertEqual(2, len(result.cases))
        self.assertIn("BROKEN_BRIDGE", findings)
        self.assertIn("UNSUPPORTED_CONCLUSION", findings)
        self.assertIn("DOC_GAP", findings)

    def test_aggregate_metrics_cover_all_hops(self) -> None:
        result = ExperimentRunner(self.config).run_benchmark(self.benchmark)

        self.assertEqual(4, result.aggregate_metrics.total_hops)
        self.assertGreater(result.aggregate_metrics.mean_hop_support, 0.0)
        self.assertGreater(result.aggregate_metrics.mean_conclusion_support, 0.0)
        self.assertGreater(result.aggregate_metrics.total_findings, 0)


if __name__ == "__main__":
    unittest.main()
