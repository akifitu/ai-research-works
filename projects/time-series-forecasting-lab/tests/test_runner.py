from __future__ import annotations

import unittest
from pathlib import Path

from time_series_forecasting_lab.dataset import load_benchmark, load_config
from time_series_forecasting_lab.runner import TimeSeriesForecastingRunner


class TimeSeriesRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        self.benchmark = load_benchmark(
            project_root / "benchmarks" / "sample_time_series_benchmark.json"
        )
        self.config = load_config(project_root / "configs" / "default_forecast.json")

    def test_runner_evaluates_each_series(self) -> None:
        result = TimeSeriesForecastingRunner(self.config).run_benchmark(self.benchmark)

        self.assertEqual("mini-time-series-forecast", result.benchmark_id)
        self.assertEqual(2, len(result.series_results))
        self.assertGreater(result.mean_mae, 0.0)
        self.assertGreaterEqual(result.mean_direction_accuracy, 0.0)

    def test_each_series_has_holdout_points(self) -> None:
        result = TimeSeriesForecastingRunner(self.config).run_benchmark(self.benchmark)

        self.assertTrue(all(len(series.points) == self.config.holdout_size for series in result.series_results))


if __name__ == "__main__":
    unittest.main()
