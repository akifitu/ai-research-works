from __future__ import annotations

from datetime import datetime, timezone

from .forecasting import backtest_series, safe_divide
from .models import ForecastConfig, ForecastExperimentResult, TimeSeriesBenchmark


class TimeSeriesForecastingRunner:
    def __init__(self, config: ForecastConfig):
        self.config = config

    def run_benchmark(self, benchmark: TimeSeriesBenchmark) -> ForecastExperimentResult:
        series_results = [backtest_series(sample, self.config) for sample in benchmark.series]
        generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        return ForecastExperimentResult(
            benchmark_id=benchmark.benchmark_id,
            benchmark_description=benchmark.description,
            config=self.config,
            series_results=series_results,
            mean_mae=safe_divide(sum(result.mae for result in series_results), len(series_results)),
            mean_smape=safe_divide(
                sum(result.smape for result in series_results),
                len(series_results),
            ),
            mean_direction_accuracy=safe_divide(
                sum(result.direction_accuracy for result in series_results),
                len(series_results),
            ),
            generated_at=generated_at,
        )
