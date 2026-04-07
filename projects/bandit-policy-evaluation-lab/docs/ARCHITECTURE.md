# Architecture

## Overview

The lab evaluates prerecorded bandit logs instead of running a live policy.
Each benchmark scenario contains:

- policy cards describing the compared strategies
- logged events with observed rewards and behavior propensities
- candidate-policy support values for the logged action

The runner evaluates each policy on the same event set, compares candidates
against the baseline, and emits policy-selection findings.

## Core Modules

- `models.py`: dataclasses for benchmarks, policies, events, metrics, and findings
- `dataset.py`: JSON loading and result serialization
- `evaluation.py`: clipped IPS, SNIPS, support-rate, regret, and segment summaries
- `metrics.py`: scenario-level and benchmark-level metric aggregation
- `runner.py`: baseline delta analysis and finding generation
- `reporting.py`: portfolio-facing HTML report rendering
- `cli.py`: command-line entry point

## Evaluation Flow

1. Load a benchmark file with scenarios and logged events.
2. Load a config file with clipping and alert thresholds.
3. For each policy in each scenario:
   - compute clipped importance weights
   - estimate IPS and SNIPS rewards
   - compute support rate and effective sample ratio
   - evaluate segment-level regret
   - combine metrics into a composite selection score
4. Compare candidate scores against the scenario baseline.
5. Serialize JSON output and render an HTML report.

## Design Choices

- Clipped IPS keeps the baseline implementation simple and auditable.
- SNIPS is included because it is a familiar offline-evaluation estimator with
  better stability properties than raw IPS on small samples.
- Segment regret is first-class because rollout decisions often fail at the
  slice level rather than in the aggregate.
- The project stays stdlib-first so the repository remains lightweight.

## Data Model

- `BanditBenchmark`: top-level benchmark metadata and scenarios
- `Scenario`: one decision surface with a baseline and candidate policies
- `LoggedEvent`: one historical decision with observed reward and propensities
- `PolicyEvaluation`: estimator outputs and composite score for one policy
- `ScenarioResult`: all policy evaluations, deltas, findings, and metrics
- `ExperimentResult`: benchmark-wide output artifact

## Extension Path

The architecture intentionally leaves room for:

- reward-model-based doubly robust evaluation
- contextual bandit slices with richer feature metadata
- confidence intervals and uncertainty-aware gating
- integration with experimentation or recommendation platforms
