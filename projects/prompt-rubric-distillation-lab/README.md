# Prompt Rubric Distillation Lab

[![License: MIT](https://img.shields.io/badge/license-MIT-0f766e.svg)](../../LICENSE)
[![Language: Python](https://img.shields.io/badge/language-Python-1d4ed8.svg)](https://www.python.org/)

`prompt-rubric-distillation-lab` is a portfolio-ready AI research project for
turning qualitative evaluation rubrics into structured scorecards. It helps
teams translate vague review language into reusable dimensions, normalized
weights, checklist questions, and machine-readable scoring artifacts.

## Research Questions

- How can freeform rubric text be normalized into stable evaluation dimensions?
- Which rubric criteria are ambiguous or underspecified?
- How should criterion weights be normalized when authors mix explicit and implicit priorities?
- How can rubric structure be made reusable before any judge model is added?

## What The Project Implements

- JSON benchmark format for qualitative rubrics
- Dimension inference for criteria such as factuality, safety, recovery, and clarity
- Ambiguity flagging for vague evaluative language
- Weight normalization across explicit and implicit criteria
- Checklist and scale-anchor generation
- HTML and JSON report generation

## Why It Is Portfolio-Worthy

- It targets evaluation design, which is a real bottleneck in LLM product work
- It creates reusable assets instead of one-off prose
- The heuristics are transparent enough to defend in a portfolio
- It leaves a clean path toward judge-model or human-label integration later

## Project Layout

```text
projects/prompt-rubric-distillation-lab
├── benchmarks/
│   └── sample_rubrics.json
├── configs/
│   └── default_distillation.json
├── docs/
│   ├── ARCHITECTURE.md
│   └── IMPLEMENTATION_PLAN.md
├── pyproject.toml
├── src/prompt_rubric_distillation_lab/
│   ├── cli.py
│   ├── dataset.py
│   ├── distillation.py
│   ├── metrics.py
│   ├── models.py
│   ├── reporting.py
│   └── runner.py
└── tests/
    ├── test_distillation.py
    └── test_runner.py
```

## Benchmark Schema

```json
{
  "benchmark_id": "mini-rubric-distillation",
  "description": "Small benchmark for rubric normalization",
  "rubrics": [
    {
      "rubric_id": "grounded-answer-review",
      "task": "Evaluate a citation-heavy answer",
      "criteria": [
        {
          "criterion_id": "crit-01",
          "text": "The answer should be factually accurate and every major claim must be supported by cited evidence.",
          "weight": 5
        }
      ]
    }
  ]
}
```

## Intended Workflow

1. Capture a qualitative evaluation rubric as JSON.
2. Run the distillation pipeline to infer dimensions and normalize weights.
3. Review ambiguity flags and checklist prompts.
4. Use the generated scorecard as the base for future human or model-based evaluation.

## Example Command

```bash
python -m prompt_rubric_distillation_lab.cli run \
  --benchmark projects/prompt-rubric-distillation-lab/benchmarks/sample_rubrics.json \
  --config projects/prompt-rubric-distillation-lab/configs/default_distillation.json \
  --output-dir reports/prompt-rubric-distillation-lab
```

## Example Findings

- `AMBIGUITY`: rubric text contains vague terms such as `clear` or `efficient`
- `WEIGHT_GAP`: the rubric mixes explicit and implicit weighting
- `GENERAL_CRITERION`: the criterion did not map strongly to a known evaluation dimension

## Extensions For Future Work

- Compare distilled scorecards against human annotation variance
- Add rubric importers from Markdown docs and spreadsheets
- Generate judge prompts from the structured scorecards
- Add calibration tooling for multi-rater evaluation workflows
