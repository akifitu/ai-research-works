from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .models import NlpExperimentResult


def result_to_dict(result: NlpExperimentResult) -> dict[str, Any]:
    return asdict(result)
