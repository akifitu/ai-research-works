# Portfolio Roadmap

This roadmap keeps the repository coherent as more AI research projects are
added. Each project should be portfolio-ready, documented, and independently
valuable on GitHub.

## Current Projects

| Status | Project | Goal |
| --- | --- | --- |
| Implemented | `citation-grounding-lab` | Evaluate whether answer claims are supported by cited source documents |
| Implemented | `tool-trajectory-audit-lab` | Audit agent/tool trajectories for loops, recovery quality, and redundant work |
| Implemented | `long-context-stress-lab` | Measure context packing quality, noise buildup, and answer drift across budget tiers |
| Implemented | `prompt-rubric-distillation-lab` | Convert qualitative evaluation rubrics into weighted scorecards and structured scoring programs |

## Planned Projects

| Status | Project | Goal |
| --- | --- | --- |
| Planned | `multi-hop-evidence-mapper` | Track evidence chains across multi-document reasoning tasks |

## Repository Rules

- Every project gets its own README, `ARCHITECTURE.md`, and `IMPLEMENTATION_PLAN.md`
- Prefer stdlib or minimal dependencies unless a project truly requires more
- Keep benchmark assets small and illustrative unless the repo is explicitly
  expanded into a dataset repository
- Do not make local model setup a prerequisite for understanding the project
