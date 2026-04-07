from __future__ import annotations

from .models import ExperimentRun, RankedRun, RegistryBenchmark, RegistryDecision, RegistryPolicy


def _metric_value(run: ExperimentRun, policy: RegistryPolicy) -> float:
    if policy.metric_name not in run.metrics:
        raise ValueError(f"Run {run.run_id} does not contain metric {policy.metric_name}")
    return run.metrics[policy.metric_name]


def validate_run(run: ExperimentRun, policy: RegistryPolicy) -> list[str]:
    warnings = []
    missing_metadata = [
        key for key in policy.required_metadata if key not in run.metadata or not run.metadata[key]
    ]
    if missing_metadata:
        warnings.append(f"missing metadata: {', '.join(missing_metadata)}")
    blocked = sorted(set(run.tags) & set(policy.blocked_tags))
    if blocked:
        warnings.append(f"blocked tags: {', '.join(blocked)}")
    return warnings


def rank_runs(runs: list[ExperimentRun], policy: RegistryPolicy) -> list[RankedRun]:
    if policy.mode not in {"max", "min"}:
        raise ValueError("policy.mode must be 'max' or 'min'")
    reverse = policy.mode == "max"
    ordered = sorted(runs, key=lambda run: _metric_value(run, policy), reverse=reverse)
    return [
        RankedRun(
            run_id=run.run_id,
            model_name=run.model_name,
            metric_value=_metric_value(run, policy),
            rank=index,
            warnings=validate_run(run, policy),
        )
        for index, run in enumerate(ordered, start=1)
    ]


def _metric_delta(candidate: ExperimentRun, incumbent: ExperimentRun | None, policy: RegistryPolicy) -> float | None:
    if incumbent is None:
        return None
    candidate_value = _metric_value(candidate, policy)
    incumbent_value = _metric_value(incumbent, policy)
    if policy.mode == "max":
        return candidate_value - incumbent_value
    return incumbent_value - candidate_value


def _find_run(runs: list[ExperimentRun], run_id: str | None) -> ExperimentRun | None:
    if run_id is None:
        return None
    return next((run for run in runs if run.run_id == run_id), None)


def _best_promotable_run(runs: list[ExperimentRun], policy: RegistryPolicy) -> ExperimentRun | None:
    ranked = rank_runs(runs, policy)
    for ranked_run in ranked:
        if not ranked_run.warnings:
            return _find_run(runs, ranked_run.run_id)
    return None


def evaluate_registry(benchmark: RegistryBenchmark, policy: RegistryPolicy) -> RegistryDecision:
    candidate = _best_promotable_run(benchmark.runs, policy)
    incumbent = _find_run(benchmark.runs, benchmark.incumbent_run_id)
    if candidate is None:
        return RegistryDecision(
            candidate_run_id=None,
            incumbent_run_id=benchmark.incumbent_run_id,
            promoted=False,
            metric_delta=None,
            warnings=["No run satisfies the registry policy."],
            rationale="All candidate runs have missing metadata or blocked tags.",
        )

    warnings = validate_run(candidate, policy)
    metric_delta = _metric_delta(candidate, incumbent, policy)
    if incumbent is None:
        return RegistryDecision(
            candidate_run_id=candidate.run_id,
            incumbent_run_id=None,
            promoted=not warnings,
            metric_delta=None,
            warnings=warnings,
            rationale="Candidate is promotable because no incumbent run is registered.",
        )

    promoted = not warnings and metric_delta is not None and metric_delta >= policy.min_improvement
    rationale = (
        "Candidate exceeds incumbent by the configured improvement threshold."
        if promoted
        else "Candidate does not exceed incumbent by the configured improvement threshold."
    )
    return RegistryDecision(
        candidate_run_id=candidate.run_id,
        incumbent_run_id=incumbent.run_id,
        promoted=promoted,
        metric_delta=metric_delta,
        warnings=warnings,
        rationale=rationale,
    )
