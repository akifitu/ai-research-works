from __future__ import annotations

from .models import AblationConfig, VariantRun, VariantScore


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def score_variant(variant: VariantRun, config: AblationConfig) -> VariantScore:
    total_tokens = variant.prompt_tokens + variant.completion_tokens
    completion_score = 1.0 if variant.completed else 0.0
    quality_score = _clamp(variant.quality_score)
    recovery_score = (
        variant.recovered_failures / variant.failed_calls if variant.failed_calls else 1.0
    )
    tool_overage = max(variant.tool_calls - config.ideal_tool_calls, 0)
    efficiency_score = _clamp(1.0 - (tool_overage / max(config.ideal_tool_calls, 1)))
    latency_score = _clamp(1.0 - (variant.latency_ms / max(config.latency_budget_ms, 1)))
    token_efficiency_score = _clamp(1.0 - (total_tokens / max(config.token_budget, 1)))
    overall_score = (
        (0.32 * completion_score)
        + (0.24 * quality_score)
        + (0.16 * recovery_score)
        + (0.12 * efficiency_score)
        + (0.08 * latency_score)
        + (0.08 * token_efficiency_score)
        - (config.loop_penalty * variant.loop_events)
    )

    return VariantScore(
        variant=variant,
        total_tokens=total_tokens,
        completion_score=round(completion_score, 4),
        quality_score=round(quality_score, 4),
        recovery_score=round(recovery_score, 4),
        efficiency_score=round(efficiency_score, 4),
        latency_score=round(latency_score, 4),
        token_efficiency_score=round(token_efficiency_score, 4),
        overall_score=round(_clamp(overall_score), 4),
    )


def changed_factors(baseline: VariantRun, candidate: VariantRun) -> list[str]:
    factors: list[str] = []
    if baseline.prompt_strategy != candidate.prompt_strategy:
        factors.append(f"prompt:{candidate.prompt_strategy}")
    if baseline.tool_policy != candidate.tool_policy:
        factors.append(f"tool:{candidate.tool_policy}")
    if baseline.retrieval_policy != candidate.retrieval_policy:
        factors.append(f"retrieval:{candidate.retrieval_policy}")
    return factors

