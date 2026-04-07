from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .models import ReliabilityResult


def result_to_dict(result: ReliabilityResult) -> dict[str, Any]:
    return asdict(result)
