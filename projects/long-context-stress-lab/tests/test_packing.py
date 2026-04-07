from __future__ import annotations

import unittest
from pathlib import Path

from long_context_stress_lab.dataset import load_benchmark
from long_context_stress_lab.packing import pack_context, relevant_coverage


class PackingTests(unittest.TestCase):
    def setUp(self) -> None:
        benchmark_path = (
            Path(__file__).resolve().parents[1]
            / "benchmarks"
            / "sample_context_benchmark.json"
        )
        self.benchmark = load_benchmark(benchmark_path)

    def test_small_budget_omits_lower_priority_relevant_context(self) -> None:
        case = self.benchmark.cases[1]
        packed = pack_context(case.context_items, 60)
        packed_ids = [item.item_id for item in packed]

        self.assertEqual(["ctx_summary"], packed_ids)
        self.assertLess(relevant_coverage(case.context_items, packed), 0.65)

    def test_large_budget_includes_relevant_items_before_noise(self) -> None:
        case = self.benchmark.cases[0]
        packed = pack_context(case.context_items, 140)
        packed_ids = [item.item_id for item in packed]

        self.assertEqual(
            ["ctx_core_dilution", "ctx_core_unsupported", "ctx_noise_history"],
            packed_ids,
        )


if __name__ == "__main__":
    unittest.main()
