from __future__ import annotations

from datetime import datetime, timezone

from .auditing import TraceAuditor
from .metrics import summarize_runs
from .models import AuditConfig, ExperimentResult, TraceBenchmark


class ExperimentRunner:
    def __init__(self, config: AuditConfig):
        self.config = config
        self.auditor = TraceAuditor(config)

    def run_benchmark(self, benchmark: TraceBenchmark) -> ExperimentResult:
        run_results = [self.auditor.audit_run(run) for run in benchmark.runs]
        aggregate_metrics = summarize_runs(run_results)
        generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        return ExperimentResult(
            benchmark_id=benchmark.benchmark_id,
            benchmark_description=benchmark.description,
            config=self.config,
            runs=run_results,
            aggregate_metrics=aggregate_metrics,
            generated_at=generated_at,
        )
