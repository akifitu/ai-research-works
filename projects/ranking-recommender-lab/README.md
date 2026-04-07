# Ranking Recommender Lab

[![License: MIT](https://img.shields.io/badge/license-MIT-0f766e.svg)](../../LICENSE)
[![Language: Python](https://img.shields.io/badge/language-Python-1d4ed8.svg)](https://www.python.org/)

`ranking-recommender-lab` is a portfolio-ready recommender-systems research
project for evaluating ranked recommendation outputs. It turns prerecorded
query-level predictions into auditable NDCG@K, MAP@K, hit-rate, catalog
coverage, long-tail exposure, and cold-start diagnostics without requiring
live serving infrastructure.

## Research Questions

- Which ranking system actually improves relevance quality over the baseline?
- Are gains concentrated on power users while cold-start users regress?
- How much diversity or catalog exploration is lost to popularity bias?
- Which recommender variant is strongest when both ranking quality and product
  coverage are evaluated together?

## What The Project Implements

- JSON benchmark format for scenarios, catalog items, systems, and queries
- Ranking metrics including Precision@K, Recall@K, MAP@K, and NDCG@K
- System-level hit rate, catalog coverage, and long-tail recommendation share
- Segment summaries for cold-start and other cohorts
- Baseline-versus-candidate comparisons and finding generation
- HTML and JSON report generation

## Why It Is Portfolio-Worthy

- It adds a high-signal recommender-systems discipline to the monorepo
- It focuses on evaluation and rollout quality rather than toy recommendation code
- It combines relevance metrics with product-facing diversity diagnostics
- It gives GitHub readers a concrete view of ranking-system tradeoffs

## Project Layout

```text
projects/ranking-recommender-lab
├── benchmarks/
│   └── sample_ranking_benchmark.json
├── configs/
│   └── default_ranking_eval.json
├── docs/
│   ├── ARCHITECTURE.md
│   └── IMPLEMENTATION_PLAN.md
├── pyproject.toml
├── src/ranking_recommender_lab/
│   ├── cli.py
│   ├── dataset.py
│   ├── evaluation.py
│   ├── metrics.py
│   ├── models.py
│   ├── reporting.py
│   └── runner.py
└── tests/
    ├── test_evaluation.py
    └── test_runner.py
```

## Benchmark Schema

```json
{
  "benchmark_id": "mini-ranking-recommender-benchmark",
  "description": "Small ranking benchmark for recommender systems",
  "scenarios": [
    {
      "scenario_id": "homepage-feed",
      "name": "Homepage ranking comparison",
      "k": 5,
      "baseline_system_id": "popularity_baseline",
      "catalog": [
        {
          "item_id": "item_01",
          "is_long_tail": false
        }
      ],
      "systems": [
        {
          "system_id": "popularity_baseline",
          "family": "popularity"
        }
      ],
      "queries": [
        {
          "query_id": "query_001",
          "segment": "cold_start",
          "relevant_items": [
            {
              "item_id": "item_07",
              "grade": 3
            }
          ],
          "predictions": {
            "popularity_baseline": ["item_01", "item_02", "item_03"]
          }
        }
      ]
    }
  ]
}
```

## Intended Workflow

1. Export ranked predictions for each system on the same query set.
2. Attach graded relevance labels for the benchmarked items.
3. Mark catalog items with long-tail or other product metadata.
4. Tune thresholds in the config file for coverage, cold-start quality, and regressions.
5. Run the benchmark to generate JSON and HTML ranking reports.
6. Review quality lift together with diversity and segment-level risks.

## Example Command

```bash
python -m ranking_recommender_lab.cli run \
  --benchmark projects/ranking-recommender-lab/benchmarks/sample_ranking_benchmark.json \
  --config projects/ranking-recommender-lab/configs/default_ranking_eval.json \
  --output-dir reports/ranking-recommender-lab
```

## Example Findings

- `WINNER`: a non-baseline system delivered the top composite score
- `BASELINE_REGRESSION`: a candidate ranked materially below the baseline
- `COLD_START_GAP`: cold-start ranking quality fell below the configured floor
- `COVERAGE_RISK`: the system touched too little of the available catalog
- `POPULARITY_BIAS`: the system exposed too little of the long-tail inventory

## Extensions For Future Work

- Add session-aware metrics and repeat-consumption penalties
- Add business-value weighting for revenue or retention sensitivity
- Add uncertainty intervals over repeated traffic slices
- Add fairness or supplier-diversity constraints to ranking analysis
