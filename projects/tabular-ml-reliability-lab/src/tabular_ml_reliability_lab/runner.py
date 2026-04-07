from __future__ import annotations

from datetime import datetime, timezone

from .analysis import analyze_reliability
from .models import ReliabilityConfig, ReliabilityResult, TabularBenchmark


class TabularReliabilityRunner:
    def __init__(self, config: ReliabilityConfig):
        self.config = config

    def run_benchmark(self, benchmark: TabularBenchmark) -> ReliabilityResult:
        baseline_profile, current_profile, findings, leakage_candidates = analyze_reliability(
            benchmark.baseline_rows,
            benchmark.current_rows,
            self.config,
        )
        generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        return ReliabilityResult(
            benchmark_id=benchmark.benchmark_id,
            benchmark_description=benchmark.description,
            config=self.config,
            baseline_profile=baseline_profile,
            current_profile=current_profile,
            drift_findings=findings,
            leakage_candidates=leakage_candidates,
            high_risk_feature_count=sum(finding.risk_level == "HIGH" for finding in findings),
            generated_at=generated_at,
        )
