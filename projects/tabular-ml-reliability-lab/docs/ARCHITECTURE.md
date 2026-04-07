# Architecture

`tabular-ml-reliability-lab` is a lightweight guardrail layer for tabular ML
systems. It does not train a model; it evaluates whether the input data and
feature set look safe enough to trust a model evaluation.

## Pipeline

1. Load baseline and current row sets from JSON.
2. Infer feature type as numeric or categorical.
3. Compute per-feature profile statistics.
4. Compare baseline/current profiles for drift and missingness deltas.
5. Flag target leakage candidates based on feature names and value identity.

## Extension Points

- Add CSV and Parquet adapters.
- Add PSI or Jensen-Shannon divergence for larger datasets.
- Add fairness slice metrics by protected attributes.
- Add model performance regression checks when labels and predictions exist.
