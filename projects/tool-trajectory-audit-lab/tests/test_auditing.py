from __future__ import annotations

import unittest
from pathlib import Path

from tool_trajectory_audit_lab.auditing import TraceAuditor
from tool_trajectory_audit_lab.dataset import load_benchmark, load_config


class TraceAuditingTests(unittest.TestCase):
    def setUp(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        self.benchmark = load_benchmark(project_root / "benchmarks" / "sample_traces.json")
        self.config = load_config(project_root / "configs" / "default_audit.json")
        self.auditor = TraceAuditor(self.config)

    def test_recovery_run_emits_failure_and_recovery_findings(self) -> None:
        result = self.auditor.audit_run(self.benchmark.runs[0])
        categories = {finding.category for finding in result.findings}

        self.assertIn("FAILURE", categories)
        self.assertIn("RECOVERY", categories)
        self.assertEqual(1, result.metrics.failure_count)
        self.assertEqual(1, result.metrics.recovered_failure_count)

    def test_loopy_run_flags_loop_empty_result_and_latency(self) -> None:
        result = self.auditor.audit_run(self.benchmark.runs[1])
        categories = {finding.category for finding in result.findings}

        self.assertIn("LOOP", categories)
        self.assertIn("EMPTY_RESULT", categories)
        self.assertIn("LATENCY", categories)
        self.assertEqual(2, result.metrics.failure_count)
        self.assertGreaterEqual(result.metrics.loop_count, 1)


if __name__ == "__main__":
    unittest.main()
