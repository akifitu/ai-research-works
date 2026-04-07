# MLOps Experiment Registry Lab

This lab adds an MLOps and research-operations project to the portfolio. It
models how experiment runs can be ranked, checked for reproducibility metadata,
and promoted only when they beat an incumbent under a transparent policy.

## Research Signal

- Experiment run registry data model
- Metric-based ranking with max/min optimization modes
- Incumbent comparison and minimum-improvement gates
- Required metadata checks for reproducibility
- Blocked tag policy for unsafe or incomplete runs

## Example

```powershell
pip install ./projects/mlops-experiment-registry-lab
mlops-experiment-registry-lab --benchmark projects/mlops-experiment-registry-lab/benchmarks/sample_registry_benchmark.json
```
