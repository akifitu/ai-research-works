from __future__ import annotations

from .models import ForecastConfig, ForecastPoint, SeriesForecastResult, TimeSeriesSample


def safe_divide(numerator: float, denominator: float) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


def moving_average_forecast(history: list[float], window_size: int) -> float:
    if not history:
        return 0.0
    window = history[-max(1, window_size):]
    return safe_divide(sum(window), len(window))


def naive_forecast(history: list[float]) -> float:
    return history[-1] if history else 0.0


def smape(actual: float, predicted: float) -> float:
    return safe_divide(abs(actual - predicted), (abs(actual) + abs(predicted)) / 2)


def _predict(history: list[float], config: ForecastConfig) -> float:
    if config.strategy == "naive":
        return naive_forecast(history)
    if config.strategy == "moving_average":
        return moving_average_forecast(history, config.window_size)
    raise ValueError(f"Unknown forecast strategy: {config.strategy}")


def _direction_accuracy(values: list[float], points: list[ForecastPoint]) -> float:
    if not points:
        return 0.0
    correct = 0
    scored = 0
    start_index = points[0].step_index
    for point in points:
        previous_actual = values[point.step_index - 1] if point.step_index > 0 else values[start_index]
        actual_direction = actual_sign(point.actual - previous_actual)
        predicted_direction = actual_sign(point.predicted - previous_actual)
        if actual_direction == 0:
            continue
        scored += 1
        correct += actual_direction == predicted_direction
    return safe_divide(correct, scored)


def actual_sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def backtest_series(sample: TimeSeriesSample, config: ForecastConfig) -> SeriesForecastResult:
    if config.holdout_size <= 0 or config.holdout_size >= len(sample.values):
        raise ValueError("holdout_size must be positive and smaller than the series length")

    train = sample.values[:-config.holdout_size]
    holdout = sample.values[-config.holdout_size:]
    history = list(train)
    points = []
    first_step = len(train)
    for offset, actual in enumerate(holdout):
        predicted = _predict(history, config)
        points.append(
            ForecastPoint(
                step_index=first_step + offset,
                actual=actual,
                predicted=predicted,
                absolute_error=abs(actual - predicted),
                smape=smape(actual, predicted),
            )
        )
        history.append(actual)

    return SeriesForecastResult(
        series_id=sample.series_id,
        points=points,
        mae=safe_divide(sum(point.absolute_error for point in points), len(points)),
        smape=safe_divide(sum(point.smape for point in points), len(points)),
        direction_accuracy=_direction_accuracy(sample.values, points),
    )
