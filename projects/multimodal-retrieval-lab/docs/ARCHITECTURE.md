# Architecture

## Overview

The lab evaluates prerecorded cross-modal rankings instead of running a live
retrieval service. Each benchmark scenario contains:

- multimodal assets identified by modality
- retrieval systems to compare
- text-to-image and image-to-text queries
- relevance labels and hard negatives for each query

The runner computes retrieval quality and robustness metrics per system,
compares candidates against the baseline, and emits rollout findings.

## Core Modules

- `models.py`: dataclasses for assets, systems, queries, metrics, and findings
- `dataset.py`: JSON loading and result serialization
- `evaluation.py`: query-level retrieval metrics and slice aggregations
- `metrics.py`: scenario-level and benchmark-level summary metrics
- `runner.py`: baseline comparison and finding generation
- `reporting.py`: HTML report rendering for portfolio presentation
- `cli.py`: command-line entry point

## Evaluation Flow

1. Load a benchmark file with scenarios, assets, systems, and queries.
2. Load a config file with `k` and alert thresholds.
3. For each system in each scenario:
   - compute Recall@K, MRR, top-1 accuracy, and median rank
   - compute gallery coverage and hard-negative hit rate
   - aggregate direction and segment slice summaries
   - combine the signals into a composite system score
4. Compare candidate scores against the baseline system.
5. Serialize JSON output and render an HTML report.

## Design Choices

- Retrieval quality is measured with both Recall@K and MRR because they capture
  different ranking behaviors.
- Hard-negative rate is first-class because retrieval systems can look good on
  aggregate recall while still surfacing confusing false matches.
- Direction and segment slices are explicit because multimodal systems often
  perform unevenly across modalities or cohorts.
- The project remains stdlib-first to keep the monorepo lightweight.

## Data Model

- `RetrievalBenchmark`: top-level benchmark metadata and scenarios
- `RetrievalScenario`: one multimodal retrieval surface with systems and queries
- `RetrievalQuery`: one text-to-image or image-to-text evaluation unit
- `SystemEvaluation`: aggregate metrics for one retrieval system
- `SliceSummary`: direction or segment summary metrics
- `ScenarioResult`: system evaluations, deltas, findings, and metrics
- `ExperimentResult`: benchmark-wide output artifact

## Extension Path

The architecture is designed to support:

- larger gallery sampling and Recall@10 style studies
- multilingual text slices and domain shift analysis
- retrieval-reranking cascades
- calibration and threshold diagnostics for production adoption
