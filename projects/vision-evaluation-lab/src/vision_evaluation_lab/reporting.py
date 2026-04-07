from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .models import VisionExperimentResult


def result_to_dict(result: VisionExperimentResult) -> dict[str, Any]:
    return asdict(result)
