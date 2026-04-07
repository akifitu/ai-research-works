from __future__ import annotations

import re

from .models import ToolTraceStep

ERROR_PATTERN = re.compile(
    r"(error:|fatal:|traceback|exception|no such file|could not resolve|permission denied)",
    re.IGNORECASE,
)
EMPTY_OUTPUT_MARKERS = {"", "none", "no matches", "no output", "[]"}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def normalize_tool_signature(step: ToolTraceStep | None) -> str:
    if step is None:
        return "unknown:"
    tool_name = (step.tool_name or "unknown").strip().lower()
    content = normalize_text(step.content)
    return f"{tool_name}:{content}"


def infer_result_status(step: ToolTraceStep) -> str:
    if step.status:
        return step.status.strip().lower()
    if ERROR_PATTERN.search(step.content):
        return "failure"
    return "success"


def is_failure_result(step: ToolTraceStep) -> bool:
    return step.kind == "tool_result" and infer_result_status(step) == "failure"


def is_empty_result(step: ToolTraceStep) -> bool:
    if step.kind != "tool_result" or infer_result_status(step) != "success":
        return False
    normalized = normalize_text(step.content)
    return normalized in EMPTY_OUTPUT_MARKERS
