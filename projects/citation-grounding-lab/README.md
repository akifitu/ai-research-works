# Citation Grounding Lab

[![License: MIT](https://img.shields.io/badge/license-MIT-0f766e.svg)](../../LICENSE)
[![Language: Python](https://img.shields.io/badge/language-Python-1d4ed8.svg)](https://www.python.org/)

`citation-grounding-lab` is a portfolio-ready AI research project for analyzing
whether generated answers are truly supported by the documents they cite. It is
designed for RAG and citation-heavy LLM workflows where traceability matters as
much as fluency.

## Research Questions

- Do answer claims actually match the evidence documents?
- Are inline citations pointing to the right sources?
- Which claims are partially supported versus contradicted?
- How can faithfulness be summarized without running a local model?

## What The Project Implements

- Sentence-level claim extraction from answer text
- Inline citation parsing for formats like `[doc_id]`
- Token-based chunk retrieval over the provided evidence set
- Support, partial-support, unsupported, and contradicted claim labeling
- Aggregate metrics for citation precision, support rate, and faithfulness
- HTML and JSON report generation for benchmark runs

## Why It Is Portfolio-Worthy

- It solves a concrete LLM evaluation problem instead of acting as a toy app
- The architecture is reusable across future experiments
- It keeps local setup light by using the Python standard library only
- It leaves room for future provider adapters, judge models, or benchmark suites

## Project Layout

```text
projects/citation-grounding-lab
├── benchmarks/
│   └── sample_benchmark.json
├── configs/
│   └── default_experiment.json
├── docs/
│   ├── ARCHITECTURE.md
│   └── IMPLEMENTATION_PLAN.md
├── pyproject.toml
├── src/citation_grounding_lab/
│   ├── claims.py
│   ├── citations.py
│   ├── cli.py
│   ├── dataset.py
│   ├── grounding.py
│   ├── metrics.py
│   ├── models.py
│   ├── reporting.py
│   ├── retrieval.py
│   ├── runner.py
│   └── text.py
└── tests/
    ├── test_claims.py
    └── test_grounding.py
```

## Benchmark Schema

The benchmark format is simple JSON:

```json
{
  "benchmark_id": "mini-citation-grounding",
  "description": "Small portfolio benchmark for grounded-answer analysis",
  "samples": [
    {
      "sample_id": "sample-01",
      "question": "Question text",
      "answer": "Generated answer with [doc_id] citations.",
      "documents": [
        {
          "doc_id": "doc_alpha",
          "title": "Document title",
          "text": "Evidence text"
        }
      ]
    }
  ]
}
```

## Intended Workflow

1. Prepare a benchmark JSON file with answer samples and evidence documents.
2. Tune chunking and threshold settings in a JSON config file.
3. Run the experiment runner to produce JSON and HTML artifacts.
4. Review unsupported or contradicted claims to refine prompts, retrieval, or citations.

## Example Command

```bash
python -m citation_grounding_lab.cli run \
  --benchmark projects/citation-grounding-lab/benchmarks/sample_benchmark.json \
  --config projects/citation-grounding-lab/configs/default_experiment.json \
  --output-dir reports/citation-grounding-lab
```

## Example Output Signals

- `SUPPORTED`: claim has strong lexical and numeric alignment with evidence
- `PARTIAL`: evidence overlaps but is incomplete or citation alignment is weak
- `UNSUPPORTED`: retriever found weak or irrelevant support
- `CONTRADICTED`: supporting-looking evidence conflicts through numbers or negation

## Extensions For Future Work

- Provider adapters for hosted LLM answer generation
- Learned rerankers or embedding retrievers
- Judge-model scoring alongside heuristics
- Multi-hop evidence graph construction
- Dataset cards and benchmark comparison dashboards
