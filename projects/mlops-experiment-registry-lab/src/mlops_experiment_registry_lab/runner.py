from __future__ import annotations

from datetime import datetime, timezone

from .models import RegistryBenchmark, RegistryPolicy, RegistryResult
from .registry import evaluate_registry, rank_runs


class ExperimentRegistryRunner:
    def __init__(self, policy: RegistryPolicy):
        self.policy = policy

    def run_benchmark(self, benchmark: RegistryBenchmark) -> RegistryResult:
        generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        return RegistryResult(
            benchmark_id=benchmark.benchmark_id,
            benchmark_description=benchmark.description,
            policy=self.policy,
            ranked_runs=rank_runs(benchmark.runs, self.policy),
            decision=evaluate_registry(benchmark, self.policy),
            generated_at=generated_at,
        )
