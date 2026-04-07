from __future__ import annotations

from collections import Counter

from .models import DriftFinding, FeatureProfile, ReliabilityConfig, Row


def safe_divide(numerator: float, denominator: float) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


def _is_missing(value: object) -> bool:
    return value is None or value == ""


def _as_float(value: object) -> float | None:
    if _is_missing(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _feature_names(rows: list[Row]) -> list[str]:
    return sorted({name for row in rows for name in row})


def profile_feature(rows: list[Row], feature: str) -> FeatureProfile:
    values = [row.get(feature) for row in rows]
    present = [value for value in values if not _is_missing(value)]
    numeric_values = [_as_float(value) for value in present]
    is_numeric = bool(present) and all(value is not None for value in numeric_values)
    missing_rate = safe_divide(len(values) - len(present), len(values))
    top_values = Counter(str(value) for value in present).most_common(5)
    return FeatureProfile(
        name=feature,
        kind="numeric" if is_numeric else "categorical",
        row_count=len(rows),
        missing_rate=missing_rate,
        distinct_count=len({str(value) for value in present}),
        mean=(
            safe_divide(sum(value for value in numeric_values if value is not None), len(numeric_values))
            if is_numeric
            else None
        ),
        top_values=dict(top_values),
    )


def profile_dataset(rows: list[Row]) -> list[FeatureProfile]:
    return [profile_feature(rows, feature) for feature in _feature_names(rows)]


def _categorical_overlap(left: FeatureProfile, right: FeatureProfile) -> float:
    left_values = set(left.top_values)
    right_values = set(right.top_values)
    return safe_divide(len(left_values & right_values), len(left_values | right_values))


def _mean_shift(left: FeatureProfile, right: FeatureProfile) -> float | None:
    if left.mean is None or right.mean is None:
        return None
    return abs(right.mean - left.mean) / max(abs(left.mean), 1.0)


def compare_profiles(
    baseline_profiles: list[FeatureProfile],
    current_profiles: list[FeatureProfile],
    config: ReliabilityConfig,
) -> list[DriftFinding]:
    baseline_by_name = {profile.name: profile for profile in baseline_profiles}
    current_by_name = {profile.name: profile for profile in current_profiles}
    findings = []
    for feature in sorted(set(baseline_by_name) | set(current_by_name)):
        baseline = baseline_by_name.get(feature)
        current = current_by_name.get(feature)
        if baseline is None or current is None:
            findings.append(
                DriftFinding(
                    feature=feature,
                    kind="schema",
                    risk_level="HIGH",
                    missing_rate_delta=0.0,
                    mean_shift=None,
                    categorical_overlap=None,
                    rationale="Feature exists in only one dataset snapshot.",
                )
            )
            continue

        missing_delta = abs(current.missing_rate - baseline.missing_rate)
        mean_shift = _mean_shift(baseline, current) if baseline.kind == "numeric" else None
        categorical_overlap = (
            _categorical_overlap(baseline, current) if baseline.kind == "categorical" else None
        )
        reasons = []
        if missing_delta >= config.missing_rate_delta_threshold:
            reasons.append("missing-rate shift")
        if mean_shift is not None and mean_shift >= config.mean_shift_threshold:
            reasons.append("numeric mean shift")
        if (
            categorical_overlap is not None
            and categorical_overlap < config.categorical_overlap_threshold
        ):
            reasons.append("categorical coverage shift")
        risk_level = "HIGH" if reasons else "LOW"
        findings.append(
            DriftFinding(
                feature=feature,
                kind=baseline.kind,
                risk_level=risk_level,
                missing_rate_delta=missing_delta,
                mean_shift=mean_shift,
                categorical_overlap=categorical_overlap,
                rationale=", ".join(reasons) if reasons else "No configured drift threshold exceeded.",
            )
        )
    return findings


def detect_leakage_candidates(rows: list[Row], target_column: str) -> list[str]:
    if not rows or target_column not in rows[0]:
        return []
    candidates = []
    target_values = [row.get(target_column) for row in rows]
    for feature in _feature_names(rows):
        if feature == target_column:
            continue
        feature_values = [row.get(feature) for row in rows]
        name_signal = target_column.lower() in feature.lower()
        value_signal = feature_values == target_values
        if name_signal or value_signal:
            candidates.append(feature)
    return sorted(candidates)


def analyze_reliability(
    baseline_rows: list[Row],
    current_rows: list[Row],
    config: ReliabilityConfig,
) -> tuple[list[FeatureProfile], list[FeatureProfile], list[DriftFinding], list[str]]:
    baseline_profile = profile_dataset(baseline_rows)
    current_profile = profile_dataset(current_rows)
    return (
        baseline_profile,
        current_profile,
        compare_profiles(baseline_profile, current_profile, config),
        detect_leakage_candidates(baseline_rows, config.target_column),
    )
