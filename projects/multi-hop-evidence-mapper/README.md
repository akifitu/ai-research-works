# Multi-Hop Evidence Mapper

[![License: MIT](https://img.shields.io/badge/license-MIT-0f766e.svg)](../../LICENSE)
[![Language: Python](https://img.shields.io/badge/language-Python-1d4ed8.svg)](https://www.python.org/)

`multi-hop-evidence-mapper` is a portfolio-ready AI research project for
analyzing reasoning chains that span multiple documents. It checks whether each
intermediate hop is supported, whether bridge entities carry cleanly across the
chain, and whether the final conclusion is grounded in the composed evidence.

## Research Questions

- Which reasoning hops are actually supported by the available documents?
- Where do bridge entities break between adjacent hops?
- Does the final conclusion stay grounded when multiple documents are composed?
- How can multi-hop evidence chains be audited without running a local model?

## What The Project Implements

- JSON benchmark format for multi-hop cases, documents, hops, and conclusion claims
- Lexical hop-to-document support scoring
- Bridge-term continuity analysis across adjacent hops
- Conclusion grounding against the union of mapped evidence
- Case-level and benchmark-level chain quality metrics
- HTML and JSON report generation

## Why It Is Portfolio-Worthy

- It targets a real failure mode in RAG and reasoning-heavy AI systems
- It produces explicit chain artifacts instead of vague pass/fail labels
- The heuristics are understandable and extensible
- It fits naturally beside the repo’s grounding and long-context labs

## Project Layout

```text
projects/multi-hop-evidence-mapper
├── benchmarks/
│   └── sample_multi_hop.json
├── configs/
│   └── default_mapping.json
├── docs/
│   ├── ARCHITECTURE.md
│   └── IMPLEMENTATION_PLAN.md
├── pyproject.toml
├── src/multi_hop_evidence_mapper/
│   ├── cli.py
│   ├── dataset.py
│   ├── mapping.py
│   ├── metrics.py
│   ├── models.py
│   ├── reporting.py
│   └── runner.py
└── tests/
    ├── test_mapping.py
    └── test_runner.py
```

## Benchmark Schema

```json
{
  "benchmark_id": "mini-multi-hop-mapper",
  "description": "Small benchmark for multi-hop reasoning analysis",
  "cases": [
    {
      "case_id": "case-01",
      "question": "Question text",
      "answer": "Final answer text",
      "documents": [
        {
          "doc_id": "doc_a",
          "title": "Document title",
          "text": "Document text"
        }
      ],
      "reasoning_hops": [
        {
          "hop_id": "hop_01",
          "claim": "Intermediate reasoning claim",
          "bridge_terms": ["entity_a", "entity_b"]
        }
      ],
      "conclusion_claim": "Composed conclusion claim"
    }
  ]
}
```

## Intended Workflow

1. Define multi-hop reasoning cases with documents and hop claims.
2. Tune support and bridge thresholds in a config file.
3. Run the mapper to produce JSON and HTML chain reports.
4. Review broken bridges or unsupported conclusions to improve retrieval and reasoning design.

## Example Command

```bash
python -m multi_hop_evidence_mapper.cli run \
  --benchmark projects/multi-hop-evidence-mapper/benchmarks/sample_multi_hop.json \
  --config projects/multi-hop-evidence-mapper/configs/default_mapping.json \
  --output-dir reports/multi-hop-evidence-mapper
```

## Example Findings

- `MISSING_HOP_SUPPORT`: a reasoning hop lacks enough document support
- `BROKEN_BRIDGE`: bridge terms do not carry across adjacent hops
- `UNSUPPORTED_CONCLUSION`: the final composed claim is weakly grounded
- `DOC_GAP`: a document contributes too little to the intended chain

## Extensions For Future Work

- Entity-aware bridge extraction instead of explicit bridge terms
- Graph visualizations for longer reasoning chains
- Hosted-model assistance for hop proposal and repair suggestions
- Benchmark comparison across retrieval or chain-of-thought strategies
