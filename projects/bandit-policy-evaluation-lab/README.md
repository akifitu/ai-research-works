# Bandit Policy Evaluation Lab

[![License: MIT](https://img.shields.io/badge/license-MIT-0f766e.svg)](../../LICENSE)
[![Language: Python](https://img.shields.io/badge/language-Python-1d4ed8.svg)](https://www.python.org/)

`bandit-policy-evaluation-lab` is a portfolio-ready reinforcement learning
research project for offline bandit policy comparison. It turns logged
interaction data into reproducible IPS and SNIPS estimates, support analysis,
segment-level risk checks, and regret-oriented policy rankings without
requiring live traffic or local model infrastructure.

## Research Questions

- Which candidate policy improves estimated reward over the current baseline?
- How much evaluation risk is hidden behind weak logging support or low
  effective sample size?
- Which policies look strong overall but collapse on sensitive segments?
- How can offline policy evaluation be made auditable enough for portfolio and
  production discussions?

## What The Project Implements

- JSON benchmark format for logged bandit scenarios and policy cards
- Offline reward estimation with clipped IPS and self-normalized IPS
- Support-rate and effective-sample diagnostics for policy reliability
- Baseline-versus-candidate delta analysis
- Segment-level regret checks for risk-sensitive rollout review
- HTML and JSON report generation

## Why It Is Portfolio-Worthy

- It adds reinforcement learning coverage without requiring a training stack
- It focuses on a real evaluation problem instead of toy action selection code
- It demonstrates applied decision-system reasoning with auditable artifacts
- It extends the monorepo into policy selection and rollout-governance concerns

## Project Layout

```text
projects/bandit-policy-evaluation-lab
├── benchmarks/
│   └── sample_bandit_benchmark.json
├── configs/
│   └── default_policy_eval.json
├── docs/
│   ├── ARCHITECTURE.md
│   └── IMPLEMENTATION_PLAN.md
├── pyproject.toml
├── src/bandit_policy_evaluation_lab/
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
  "benchmark_id": "mini-bandit-policy-benchmark",
  "description": "Small offline policy evaluation benchmark",
  "scenarios": [
    {
      "scenario_id": "homepage-recommendations",
      "name": "Homepage recommendation slot policy comparison",
      "baseline_policy_id": "epsilon_010",
      "policies": [
        {
          "policy_id": "epsilon_010",
          "family": "epsilon_greedy",
          "exploration_rate": 0.10
        }
      ],
      "events": [
        {
          "event_id": "evt_001",
          "action_taken": "science",
          "reward": 1.0,
          "oracle_reward": 1.0,
          "logging_propensity": 0.25,
          "segment": "new_user",
          "policy_support": {
            "epsilon_010": 0.30,
            "greedy_personalized": 0.70
          }
        }
      ]
    }
  ]
}
```

## Intended Workflow

1. Export logged interaction data with propensities for the behavior policy.
2. Add target-policy support values for the logged action under each candidate.
3. Tune clipping and alert thresholds in the config file.
4. Run the benchmark to generate JSON and HTML policy evaluation reports.
5. Review reward lift, support risk, and segment-level regret before rollout.

## Example Command

```bash
python -m bandit_policy_evaluation_lab.cli run \
  --benchmark projects/bandit-policy-evaluation-lab/benchmarks/sample_bandit_benchmark.json \
  --config projects/bandit-policy-evaluation-lab/configs/default_policy_eval.json \
  --output-dir reports/bandit-policy-evaluation-lab
```

## Example Findings

- `WINNER`: a non-baseline policy delivered the best composite score
- `REGRET_ALERT`: estimated regret stayed too high versus the oracle reward
- `SUPPORT_GAP`: the logged data poorly covered the candidate policy
- `VARIANCE_RISK`: effective sample size fell too low for stable evaluation
- `SEGMENT_DROP`: a policy degraded sharply on a specific segment
- `BASELINE_REGRESSION`: a candidate scored materially below the baseline

## Extensions For Future Work

- Add doubly robust estimators with learned reward models
- Import real event logs from experimentation platforms
- Track confidence intervals via bootstrap resampling
- Add fairness or business-constraint overlays to segment diagnostics
