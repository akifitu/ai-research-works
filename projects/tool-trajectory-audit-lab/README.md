# Tool Trajectory Audit Lab

[![License: MIT](https://img.shields.io/badge/license-MIT-0f766e.svg)](../../LICENSE)
[![Language: Python](https://img.shields.io/badge/language-Python-1d4ed8.svg)](https://www.python.org/)

`tool-trajectory-audit-lab` is a portfolio-ready AI research project for
auditing agent and tool execution traces. It evaluates whether an agentic
workflow gets stuck in loops, recovers from failures, wastes tool calls, or
accumulates latency in ways that would make the system unreliable in practice.

## Research Questions

- How often do agent traces repeat the same tool call without adapting?
- When a tool call fails, does the trajectory recover or keep looping?
- Which runs are operationally efficient versus brittle?
- How can trace quality be summarized without replaying the full system?

## What The Project Implements

- JSON benchmark format for agent and tool traces
- Step normalization for repeated command/query detection
- Failure, loop, empty-result, and latency heuristics
- Recovery analysis after failed tool interactions
- Run-level and benchmark-level efficiency metrics
- HTML and JSON reporting for portfolio presentation

## Why It Is Portfolio-Worthy

- It targets a concrete agent reliability problem that is current in LLM systems
- The output is useful even before any live agent runtime is connected
- The heuristics are transparent and debuggable
- The benchmark structure can grow into a richer evaluation suite over time

## Project Layout

```text
projects/tool-trajectory-audit-lab
├── benchmarks/
│   └── sample_traces.json
├── configs/
│   └── default_audit.json
├── docs/
│   ├── ARCHITECTURE.md
│   └── IMPLEMENTATION_PLAN.md
├── pyproject.toml
├── src/tool_trajectory_audit_lab/
│   ├── auditing.py
│   ├── cli.py
│   ├── dataset.py
│   ├── metrics.py
│   ├── models.py
│   ├── normalization.py
│   ├── reporting.py
│   └── runner.py
└── tests/
    ├── test_auditing.py
    └── test_runner.py
```

## Benchmark Schema

```json
{
  "benchmark_id": "mini-tool-trace-audit",
  "description": "Small portfolio benchmark for agent trajectory auditing",
  "runs": [
    {
      "run_id": "trace-01",
      "task": "Debug a CI path issue",
      "steps": [
        {
          "step_id": "step-01",
          "kind": "tool_call",
          "tool_name": "sed",
          "content": "sed -n '1,120p' .github/workflow/ci.yml"
        }
      ]
    }
  ]
}
```

## Intended Workflow

1. Export or write an agent trace benchmark as JSON.
2. Tune thresholds for loops, recovery windows, and latency in a config file.
3. Run the audit pipeline to generate JSON and HTML artifacts.
4. Review loop, failure, and recovery findings to harden the workflow design.

## Example Command

```bash
python -m tool_trajectory_audit_lab.cli run \
  --benchmark projects/tool-trajectory-audit-lab/benchmarks/sample_traces.json \
  --config projects/tool-trajectory-audit-lab/configs/default_audit.json \
  --output-dir reports/tool-trajectory-audit-lab
```

## Example Findings

- `LOOP`: repeated identical tool calls without strategy change
- `FAILURE`: tool result returned an explicit error condition
- `RECOVERY`: a failed action was corrected within the recovery window
- `EMPTY_RESULT`: repeated successful calls produced no useful output
- `LATENCY`: a step exceeded the configured duration threshold

## Extensions For Future Work

- Correlate audit outcomes with final task success labels
- Add trace import adapters for real agent frameworks
- Model branching, parallel tool use, and retry backoff behavior
- Add trajectory quality leaderboards across prompting strategies
