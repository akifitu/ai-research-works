from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .models import RegistryResult


def result_to_dict(result: RegistryResult) -> dict[str, Any]:
    return asdict(result)
