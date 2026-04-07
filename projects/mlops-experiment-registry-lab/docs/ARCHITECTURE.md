# Architecture

`mlops-experiment-registry-lab` is a small policy engine for experiment
promotion. It is useful in a research portfolio because it shows that model
selection is not just metric sorting; reproducibility metadata and release
guardrails are part of trustworthy AI engineering.

## Pipeline

1. Load experiment runs and a registry policy from JSON.
2. Rank runs by a configured metric and optimization mode.
3. Compare the best candidate against the current incumbent.
4. Check required metadata and blocked tags.
5. Produce a promotion decision with warnings and rationale.

## Extension Points

- Add model-card generation.
- Add dataset lineage graph checks.
- Add approval workflows for human review.
- Add fairness, latency, and cost gates as multi-objective criteria.
