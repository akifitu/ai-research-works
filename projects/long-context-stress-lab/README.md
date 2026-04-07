# Long Context Stress Lab

[![License: MIT](https://img.shields.io/badge/license-MIT-0f766e.svg)](../../LICENSE)
[![Language: Python](https://img.shields.io/badge/language-Python-1d4ed8.svg)](https://www.python.org/)

`long-context-stress-lab` is a portfolio-ready AI research project for studying
what happens when prompts grow from manageable contexts to large, noisy windows.
It focuses on context packing quality, relevant evidence retention, noise
buildup, and answer drift across budget tiers.

## Research Questions

- Which relevant passages survive as context budgets change?
- At what point does irrelevant context begin to dominate the window?
- Do larger context budgets improve alignment or trigger answer drift?
- How can long-context failure modes be analyzed without running a local model?

## What The Project Implements

- JSON benchmark format for context items, reference answers, and budget-tier snapshots
- Greedy context packing under token budgets
- Relevant coverage and noise-ratio analysis
- Reference alignment, answer support, and unsupported insertion scoring
- Budget-to-budget answer drift detection
- HTML and JSON report generation

## Why It Is Portfolio-Worthy

- It targets a real LLM systems problem instead of a generic text utility
- The benchmark format is reusable across future long-context studies
- It remains lightweight and inspectable by using only the Python standard library
- The outputs are easy to present as research-engineering artifacts on GitHub

## Project Layout

```text
projects/long-context-stress-lab
├── benchmarks/
│   └── sample_context_benchmark.json
├── configs/
│   └── default_stress.json
├── docs/
│   ├── ARCHITECTURE.md
│   └── IMPLEMENTATION_PLAN.md
├── pyproject.toml
├── src/long_context_stress_lab/
│   ├── cli.py
│   ├── dataset.py
│   ├── drift.py
│   ├── metrics.py
│   ├── models.py
│   ├── packing.py
│   ├── reporting.py
│   └── runner.py
└── tests/
    ├── test_packing.py
    └── test_runner.py
```

## Benchmark Schema

```json
{
  "benchmark_id": "mini-long-context-stress",
  "description": "Small benchmark for long-context stress analysis",
  "cases": [
    {
      "case_id": "case-01",
      "question": "Question text",
      "reference_answer": "Reference answer text",
      "context_items": [
        {
          "item_id": "ctx_01",
          "title": "Passage title",
          "estimated_tokens": 42,
          "priority": 100,
          "relevance": true,
          "text": "Context text"
        }
      ],
      "answer_snapshots": [
        {
          "snapshot_id": "budget_80",
          "budget_tokens": 80,
          "answer": "Recorded answer for this budget"
        }
      ]
    }
  ]
}
```

## Intended Workflow

1. Write a benchmark with context items and recorded answer snapshots.
2. Tune thresholds for coverage, dilution, and drift in a config file.
3. Run the analysis to produce JSON and HTML artifacts.
4. Use the findings to redesign retrieval, ordering, truncation, or answer policies.

## Example Command

```bash
python -m long_context_stress_lab.cli run \
  --benchmark projects/long-context-stress-lab/benchmarks/sample_context_benchmark.json \
  --config projects/long-context-stress-lab/configs/default_stress.json \
  --output-dir reports/long-context-stress-lab
```

## Example Findings

- `OVERFLOW`: relevant context could not fit into the budget
- `DILUTION`: irrelevant passages dominated too much of the packed window
- `DRIFT`: a larger budget answer aligned worse with the reference than the prior tier
- `UNSUPPORTED_INSERTION`: the answer introduced tokens not supported by packed context

## Extensions For Future Work

- Compare packing policies such as recency-first or section-aware ordering
- Track position-sensitive loss when relevant passages are buried late in context
- Add hosted-model adapters for automatically generating answer snapshots
- Build dashboards comparing context strategies across experiments
