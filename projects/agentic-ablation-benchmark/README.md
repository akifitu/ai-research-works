# Agentic Ablation Benchmark

[![License: MIT](https://img.shields.io/badge/license-MIT-0f766e.svg)](../../LICENSE)
[![Language: Python](https://img.shields.io/badge/language-Python-1d4ed8.svg)](https://www.python.org/)

`agentic-ablation-benchmark` is a portfolio-ready AI research project for
comparing agent variants across common tasks. It turns prerecorded task runs
into structured ablation comparisons over prompt strategy, tool policy,
retrieval policy, completion quality, recovery behavior, latency, and token
cost.

## Research Questions

- Which agent variant wins on task completion without overpaying in tokens or latency?
- How much do prompt strategy, tool policy, or retrieval policy changes move performance?
- Which variants recover cleanly from failures, and which variants loop or regress?
- How can agent ablations be analyzed without replaying the live system?

## What The Project Implements

- JSON benchmark format for tasks and agent variants
- Composite scoring across completion, quality, recovery, efficiency, latency, and token cost
- Baseline-versus-variant delta analysis
- Task-level winner selection and regression flags
- Aggregate factor summaries for prompt, tool-policy, and retrieval changes
- HTML and JSON report generation

## Why It Is Portfolio-Worthy

- It targets a real agent evaluation problem instead of another toy demo
- It produces reusable benchmark artifacts rather than one-off notes
- It helps explain agent tradeoffs in a defensible, auditable way
- It extends the repository from individual diagnostics into controlled comparison

## Project Layout

```text
projects/agentic-ablation-benchmark
├── benchmarks/
│   └── sample_ablation_benchmark.json
├── configs/
│   └── default_ablation.json
├── docs/
│   ├── ARCHITECTURE.md
│   └── IMPLEMENTATION_PLAN.md
├── pyproject.toml
├── src/agentic_ablation_benchmark/
│   ├── cli.py
│   ├── dataset.py
│   ├── metrics.py
│   ├── models.py
│   ├── reporting.py
│   ├── runner.py
│   └── scoring.py
└── tests/
    ├── test_runner.py
    └── test_scoring.py
```

## Benchmark Schema

```json
{
  "benchmark_id": "mini-agentic-ablation",
  "description": "Small benchmark for comparing agent variants",
  "tasks": [
    {
      "task_id": "task_01",
      "name": "Fix a CI workflow path issue",
      "baseline_variant_id": "baseline",
      "variants": [
        {
          "variant_id": "baseline",
          "prompt_strategy": "default",
          "tool_policy": "default",
          "retrieval_policy": "none",
          "completed": true,
          "quality_score": 0.78,
          "tool_calls": 6,
          "failed_calls": 1,
          "recovered_failures": 1,
          "loop_events": 0,
          "latency_ms": 4100,
          "prompt_tokens": 820,
          "completion_tokens": 360
        }
      ]
    }
  ]
}
```

## Intended Workflow

1. Record or transcribe task runs into the benchmark JSON format.
2. Tune score weights and budgets in the config file.
3. Run the benchmark to produce JSON and HTML ablation reports.
4. Compare deltas against baseline to decide which agent policy is worth shipping.

## Example Command

```bash
python -m agentic_ablation_benchmark.cli run \
  --benchmark projects/agentic-ablation-benchmark/benchmarks/sample_ablation_benchmark.json \
  --config projects/agentic-ablation-benchmark/configs/default_ablation.json \
  --output-dir reports/agentic-ablation-benchmark
```

## Example Findings

- `REGRESSION`: a variant scored materially below the baseline
- `WINNER`: a variant delivered the best composite score on the task
- `LOOP_RISK`: loop events or tool inefficiency dominated the run
- `RECOVERY_GAP`: failures were not recovered reliably
- `COST_SPIKE`: the run exceeded token or latency budgets

## Extensions For Future Work

- Add significance analysis across repeated runs
- Add real trace importers from agent frameworks
- Track factor interactions beyond single-axis deltas
- Add hosted-model judge inputs for final answer quality

