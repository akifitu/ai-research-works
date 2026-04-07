# Architecture

`time-series-forecasting-lab` separates benchmark loading, forecasting, metric
calculation, and reporting. The baseline intentionally uses simple methods so
the evaluation harness remains easy to inspect.

## Pipeline

1. Load named time-series samples from JSON.
2. Hold out the last N observations for backtesting.
3. Generate one-step predictions using a configured baseline.
4. Roll actual observations back into history after each step.
5. Aggregate MAE, SMAPE, and direction accuracy across series.

## Extension Points

- Add seasonal naive baselines.
- Add walk-forward cross-validation splits.
- Add exogenous regressors and holiday features.
- Add probabilistic interval coverage metrics.
