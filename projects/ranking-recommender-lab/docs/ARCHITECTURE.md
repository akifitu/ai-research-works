# Architecture

## Overview

The lab evaluates prerecorded recommendation rankings instead of training or
serving a recommender model. Each benchmark scenario contains:

- a small catalog annotated with long-tail flags
- a set of recommendation systems to compare
- labeled queries with graded relevance judgments
- prediction lists for each system on the same queries

The runner computes ranking quality, diversity, and coverage metrics per
system, compares the results against the scenario baseline, and emits rollout
findings.

## Core Modules

- `models.py`: dataclasses for catalogs, queries, systems, metrics, and findings
- `dataset.py`: JSON loading and result serialization
- `evaluation.py`: query-level ranking metrics and aggregate diagnostics
- `metrics.py`: scenario-level and benchmark-level summary metrics
- `runner.py`: baseline comparison and finding generation
- `reporting.py`: HTML report rendering for portfolio presentation
- `cli.py`: command-line entry point

## Evaluation Flow

1. Load a benchmark file with scenarios, systems, and labeled queries.
2. Load a config file with `k`, coverage thresholds, and cold-start cutoffs.
3. For each system in each scenario:
   - compute Precision@K, Recall@K, MAP@K, and NDCG@K
   - compute hit rate, catalog coverage, and long-tail share
   - aggregate segment-level metrics for cold-start and other cohorts
   - combine the metrics into a composite score
4. Compare candidate scores against the baseline system.
5. Serialize JSON output and render an HTML report.

## Design Choices

- Graded relevance allows the lab to demonstrate NDCG rather than binary-only metrics.
- Coverage and long-tail share are first-class because ranking quality alone
  often hides product and marketplace tradeoffs.
- Segment summaries are explicit because cold-start failures are a common
  deployment risk in recommender systems.
- The project remains stdlib-first to keep the portfolio lightweight.

## Data Model

- `RankingBenchmark`: top-level benchmark metadata and scenarios
- `RankingScenario`: one recommendation surface with a baseline and candidates
- `RankingQuery`: one labeled query or user-context snapshot
- `SystemEvaluation`: aggregate evaluation for one ranking system
- `SegmentSummary`: cohort-level quality and diversity metrics
- `ScenarioResult`: system evaluations, deltas, findings, and metrics
- `ExperimentResult`: benchmark-wide output artifact

## Extension Path

The architecture is designed to support future additions such as:

- temporal holdouts and seasonality slices
- business-value-weighted ranking objectives
- exposure fairness constraints
- off-policy evaluation for recommenders with logged propensities
