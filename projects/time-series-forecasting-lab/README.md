# Time Series Forecasting Lab

This lab adds a data-science forecasting project to the AI research portfolio.
It implements simple but reliable rolling backtests that can later be replaced
with ARIMA, Prophet, gradient boosting, or sequence models.

## Research Signal

- Rolling one-step backtests
- Moving-average and naive forecast baselines
- MAE and SMAPE metrics
- Direction accuracy for trend-sensitive use cases
- JSON benchmark runner for reproducible comparisons

## Example

```powershell
pip install ./projects/time-series-forecasting-lab
time-series-forecasting-lab --benchmark projects/time-series-forecasting-lab/benchmarks/sample_time_series_benchmark.json
```
