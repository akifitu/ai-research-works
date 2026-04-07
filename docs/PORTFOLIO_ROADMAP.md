# Portfolio Roadmap

This roadmap keeps the repository coherent as more AI research projects are
added. Each project should be portfolio-ready, documented, and independently
valuable on GitHub.

## Current Projects

| Status | Project | Goal |
| --- | --- | --- |
| Implemented | `citation-grounding-lab` | Evaluate whether answer claims are supported by cited source documents |
| Implemented | `tool-trajectory-audit-lab` | Audit agent/tool trajectories for loops, recovery quality, and redundant work |
| Implemented | `agentic-ablation-benchmark` | Compare prompt, tool-policy, and retrieval variants across common agent task sets |
| Implemented | `bandit-policy-evaluation-lab` | Evaluate offline bandit policies with IPS/SNIPS estimates, support diagnostics, and regret analysis |
| Implemented | `ranking-recommender-lab` | Evaluate recommendation rankings with NDCG@K, MAP@K, coverage, long-tail, and cold-start slices |
| Implemented | `long-context-stress-lab` | Measure context packing quality, noise buildup, and answer drift across budget tiers |
| Implemented | `prompt-rubric-distillation-lab` | Convert qualitative evaluation rubrics into weighted scorecards and structured scoring programs |
| Implemented | `multi-hop-evidence-mapper` | Track reasoning hops, bridge entities, and conclusion support across multi-document evidence chains |
| Implemented | `vision-evaluation-lab` | Evaluate computer vision classification and detection outputs with IoU and class metrics |
| Implemented | `nlp-semantic-evaluation-lab` | Score NLP outputs with lexical similarity, entity F1, and intent accuracy |
| Implemented | `tabular-ml-reliability-lab` | Audit tabular ML datasets for drift, missingness, and leakage candidates |
| Implemented | `time-series-forecasting-lab` | Run rolling forecasting backtests with MAE, SMAPE, and direction accuracy |
| Implemented | `mlops-experiment-registry-lab` | Rank experiment runs and enforce reproducibility-aware promotion gates |

## Planned Projects

| Status | Project | Goal |
| --- | --- | --- |
| Planned | `multimodal-retrieval-lab` | Add multimodal AI coverage with image/text retrieval quality checks |
| Planned | `graph-representation-lab` | Add graph ML coverage with link prediction splits and leakage checks |
| Planned | `speech-transcription-eval-lab` | Add speech AI coverage with WER/CER and timestamp drift analysis |

## Repository Rules

- Every project gets its own README, `ARCHITECTURE.md`, and `IMPLEMENTATION_PLAN.md`
- Prefer stdlib or minimal dependencies unless a project truly requires more
- Keep benchmark assets small and illustrative unless the repo is explicitly
  expanded into a dataset repository
- Do not make local model setup a prerequisite for understanding the project
- Keep the discipline map in `docs/AI_DISCIPLINE_MAP.md` aligned with implemented labs
