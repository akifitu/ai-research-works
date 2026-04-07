from __future__ import annotations

import unittest

from time_series_forecasting_lab.forecasting import moving_average_forecast, smape


class ForecastingMetricTests(unittest.TestCase):
    def test_moving_average_uses_window(self) -> None:
        self.assertEqual(4.0, moving_average_forecast([1, 2, 3, 4, 5], window_size=3))

    def test_smape_handles_zero_denominator(self) -> None:
        self.assertEqual(0.0, smape(0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
