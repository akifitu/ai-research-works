# Tabular ML Reliability Lab

This lab adds a classic machine-learning reliability project to the portfolio.
It focuses on the checks that should surround any tabular classifier or
regressor: data profiling, drift signals, missingness shifts, categorical
coverage, and leakage-candidate detection.

## Research Signal

- Baseline/current dataset comparison
- Numeric mean-shift drift checks
- Categorical coverage overlap checks
- Missing-rate drift detection
- Target leakage candidate flags
- Dependency-free JSON benchmark runner

## Example

```powershell
pip install ./projects/tabular-ml-reliability-lab
tabular-ml-reliability-lab --benchmark projects/tabular-ml-reliability-lab/benchmarks/sample_tabular_benchmark.json
```
