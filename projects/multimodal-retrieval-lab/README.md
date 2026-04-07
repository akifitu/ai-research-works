# Multimodal Retrieval Lab

[![License: MIT](https://img.shields.io/badge/license-MIT-0f766e.svg)](../../LICENSE)
[![Language: Python](https://img.shields.io/badge/language-Python-1d4ed8.svg)](https://www.python.org/)

`multimodal-retrieval-lab` is a portfolio-ready multimodal AI research project
for evaluating image-text retrieval systems. It turns prerecorded cross-modal
rankings into auditable Recall@K, MRR, coverage, hard-negative robustness, and
slice-level diagnostics without requiring local model setup or live inference.

## Research Questions

- Which retrieval system actually improves text-to-image and image-to-text retrieval quality?
- Are gains consistent across both retrieval directions or concentrated in one modality?
- Does the system collapse on hard negatives even when aggregate recall looks good?
- Which model is strongest when ranking quality and gallery coverage are considered together?

## What The Project Implements

- JSON benchmark format for assets, systems, and cross-modal queries
- Query-level Recall@K, MRR, top-1 accuracy, and median rank analysis
- Gallery coverage and hard-negative hit-rate diagnostics
- Direction and segment slice summaries for retrieval robustness
- Baseline-versus-candidate comparisons with rollout findings
- HTML and JSON report generation

## Why It Is Portfolio-Worthy

- It adds a real multimodal evaluation problem instead of another placeholder demo
- It shows how to evaluate retrieval pipelines without depending on heavy model infrastructure
- It combines ranking quality with robustness and operational coverage signals
- It rounds out the monorepo with cross-modal AI coverage that GitHub reviewers can inspect quickly

## Project Layout

```text
projects/multimodal-retrieval-lab
├── benchmarks/
│   └── sample_multimodal_benchmark.json
├── configs/
│   └── default_retrieval_eval.json
├── docs/
│   ├── ARCHITECTURE.md
│   └── IMPLEMENTATION_PLAN.md
├── pyproject.toml
├── src/multimodal_retrieval_lab/
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
  "benchmark_id": "mini-multimodal-retrieval",
  "description": "Small image-text retrieval benchmark",
  "scenarios": [
    {
      "scenario_id": "fashion-lookbook",
      "name": "Fashion lookbook retrieval comparison",
      "k": 3,
      "baseline_system_id": "clip_baseline",
      "assets": [
        {
          "asset_id": "img_red_coat",
          "modality": "image"
        },
        {
          "asset_id": "txt_red_coat",
          "modality": "text"
        }
      ],
      "systems": [
        {
          "system_id": "clip_baseline",
          "family": "dual_encoder"
        }
      ],
      "queries": [
        {
          "query_id": "query_001",
          "direction": "text_to_image",
          "segment": "cold_start",
          "relevant_target_ids": ["img_red_coat"],
          "hard_negative_ids": ["img_blue_denim"],
          "predictions": {
            "clip_baseline": ["img_red_coat", "img_blue_denim", "img_green_jacket"]
          }
        }
      ]
    }
  ]
}
```

## Intended Workflow

1. Export ranked retrieval outputs for every system on the same query set.
2. Attach the known relevant targets and hard negatives for each query.
3. Tune thresholds for coverage, hard-negative tolerance, and slice quality in the config file.
4. Run the benchmark to generate JSON and HTML retrieval reports.
5. Review bidirectional quality, robustness, and segment-level gaps before rollout.

## Example Command

```bash
python -m multimodal_retrieval_lab.cli run \
  --benchmark projects/multimodal-retrieval-lab/benchmarks/sample_multimodal_benchmark.json \
  --config projects/multimodal-retrieval-lab/configs/default_retrieval_eval.json \
  --output-dir reports/multimodal-retrieval-lab
```

## Example Findings

- `WINNER`: a non-baseline retrieval system delivered the best composite score
- `BASELINE_REGRESSION`: a candidate scored materially below the baseline
- `COVERAGE_RISK`: too little of the retrieval gallery was surfaced
- `HARD_NEGATIVE_DRIFT`: hard negatives appeared too often in top-k results
- `DIRECTION_GAP`: text-to-image or image-to-text quality fell below the floor
- `SEGMENT_DROP`: a specific traffic segment lagged behind the expected recall floor

## Extensions For Future Work

- Add Recall@1 and Recall@10 leaderboards across larger galleries
- Add score calibration or threshold analysis for retrieval confidence
- Add multilingual text slices and domain-shift robustness checks
- Add reranking-aware evaluation on top of dual-encoder candidates
