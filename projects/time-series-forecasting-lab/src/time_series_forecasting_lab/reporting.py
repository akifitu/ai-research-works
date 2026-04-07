from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .models import ForecastExperimentResult


def result_to_dict(result: ForecastExperimentResult) -> dict[str, Any]:
    return asdict(result)
