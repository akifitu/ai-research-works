# Implementation Plan

## Goal

Build a portfolio-ready offline bandit evaluation lab that compares candidate
policies using logged interaction data, importance weighting, regret analysis,
and segment-level diagnostics.

## Step-by-Step Plan

1. Define a benchmark format for scenarios, policies, and logged events.
2. Define a compact config surface for clipping and alert thresholds.
3. Implement typed dataclasses for policies, events, results, and findings.
4. Implement clipped IPS and SNIPS estimators with effective-sample analysis.
5. Add scenario runner logic for baseline deltas and alert generation.
6. Add aggregate metrics and HTML/JSON reporting.
7. Add sample benchmark data and unit tests for deterministic review.
8. Wire the project into the monorepo README, roadmap, and CI matrix.

## Non-Goals

- Online learning or live traffic exploration
- Heavy RL frameworks or environment simulators
- Confidence interval estimation through repeated resampling
- Local model setup or reward-model training

## Future Expansion

- Doubly robust and switch estimators
- Contextual feature import for richer segment slicing
- Bootstrap uncertainty estimates
- Counterfactual policy dashboards and governance rules
