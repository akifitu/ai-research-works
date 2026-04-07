from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TimeSeriesSample:
    series_id: str
    values: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TimeSeriesBenchmark:
    benchmark_id: str
    description: str
    series: list[TimeSeriesSample]


@dataclass(frozen=True)
class ForecastConfig:
    experiment_name: str = "baseline-time-series-forecast"
    strategy: str = "moving_average"
    window_size: int = 3
    holdout_size: int = 4

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ForecastConfig":
        return cls(
            experiment_name=str(raw.get("experiment_name", cls.experiment_name)),
            strategy=str(raw.get("strategy", cls.strategy)),
            window_size=int(raw.get("window_size", cls.window_size)),
            holdout_size=int(raw.get("holdout_size", cls.holdout_size)),
        )


@dataclass(frozen=True)
class ForecastPoint:
    step_index: int
    actual: float
    predicted: float
    absolute_error: float
    smape: float


@dataclass(frozen=True)
class SeriesForecastResult:
    series_id: str
    points: list[ForecastPoint]
    mae: float
    smape: float
    direction_accuracy: float


@dataclass(frozen=True)
class ForecastExperimentResult:
    benchmark_id: str
    benchmark_description: str
    config: ForecastConfig
    series_results: list[SeriesForecastResult]
    mean_mae: float
    mean_smape: float
    mean_direction_accuracy: float
    generated_at: str
