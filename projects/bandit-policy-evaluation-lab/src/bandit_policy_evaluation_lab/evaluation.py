from __future__ import annotations

from collections import defaultdict
from statistics import fmean

from .models import LoggedEvent, PolicyCard, PolicyEvaluation, PolicyEvalConfig, SegmentSummary


def _safe_mean(values: list[float]) -> float:
    return fmean(values) if values else 0.0


def _clipped_weight(event: LoggedEvent, policy_id: str, clip: float) -> float:
    target_propensity = max(0.0, event.policy_support.get(policy_id, 0.0))
    if event.logging_propensity <= 0.0:
        return 0.0
    return min(target_propensity / event.logging_propensity, clip)


def _normalized_score(value: float, threshold: float) -> float:
    if threshold <= 0.0:
        return 1.0
    return max(0.0, min(1.0, value / threshold))


def _inverse_penalty_score(value: float, threshold: float) -> float:
    if threshold <= 0.0:
        return 1.0
    return max(0.0, min(1.0, 1.0 - (value / threshold)))


def _segment_summary(
    policy_id: str,
    segment: str,
    events: list[LoggedEvent],
    config: PolicyEvalConfig,
) -> SegmentSummary:
    weights = [_clipped_weight(event, policy_id, config.weight_clip) for event in events]
    weighted_rewards = [weight * event.reward for event, weight in zip(events, weights)]
    supported_events = sum(event.policy_support.get(policy_id, 0.0) > 0.0 for event in events)
    total_weight = sum(weights)
    oracle_mean = _safe_mean([event.oracle_reward for event in events])
    snips_reward = (sum(weighted_rewards) / total_weight) if total_weight > 0.0 else 0.0
    ips_reward = (sum(weighted_rewards) / len(events)) if events else 0.0
    return SegmentSummary(
        segment=segment,
        event_count=len(events),
        support_rate=round(supported_events / len(events), 4) if events else 0.0,
        ips_reward=round(ips_reward, 4),
        snips_reward=round(snips_reward, 4),
        regret_estimate=round(max(0.0, oracle_mean - snips_reward), 4),
    )


def evaluate_policy(
    policy: PolicyCard,
    events: list[LoggedEvent],
    config: PolicyEvalConfig,
) -> PolicyEvaluation:
    weights = [_clipped_weight(event, policy.policy_id, config.weight_clip) for event in events]
    weighted_rewards = [weight * event.reward for event, weight in zip(events, weights)]
    total_weight = sum(weights)
    sum_weight_squares = sum(weight * weight for weight in weights)
    oracle_mean = _safe_mean([event.oracle_reward for event in events])
    supported_events = sum(event.policy_support.get(policy.policy_id, 0.0) > 0.0 for event in events)

    support_rate = (supported_events / len(events)) if events else 0.0
    ips_reward = (sum(weighted_rewards) / len(events)) if events else 0.0
    snips_reward = (sum(weighted_rewards) / total_weight) if total_weight > 0.0 else 0.0
    effective_sample_ratio = (
        (total_weight * total_weight) / (len(events) * sum_weight_squares)
        if events and sum_weight_squares > 0.0
        else 0.0
    )
    regret_estimate = max(0.0, oracle_mean - snips_reward)

    reward_score = min(1.0, snips_reward)
    ips_score = min(1.0, ips_reward)
    support_score = _normalized_score(support_rate, config.support_floor)
    stability_score = _normalized_score(
        effective_sample_ratio,
        config.min_effective_sample_ratio,
    )
    regret_score = _inverse_penalty_score(
        regret_estimate,
        config.regret_alert_threshold,
    )
    overall_score = round(
        (0.45 * reward_score)
        + (0.15 * ips_score)
        + (0.15 * support_score)
        + (0.15 * stability_score)
        + (0.10 * regret_score),
        4,
    )

    segment_buckets: dict[str, list[LoggedEvent]] = defaultdict(list)
    for event in events:
        segment_buckets[event.segment].append(event)

    segment_summaries = [
        _segment_summary(policy.policy_id, segment, segment_events, config)
        for segment, segment_events in sorted(segment_buckets.items())
    ]

    return PolicyEvaluation(
        policy=policy,
        event_count=len(events),
        support_rate=round(support_rate, 4),
        ips_reward=round(ips_reward, 4),
        snips_reward=round(snips_reward, 4),
        effective_sample_ratio=round(effective_sample_ratio, 4),
        max_weight=round(max(weights, default=0.0), 4),
        regret_estimate=round(regret_estimate, 4),
        overall_score=overall_score,
        segment_summaries=segment_summaries,
    )
