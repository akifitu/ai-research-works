# AI Discipline Map

This map keeps the portfolio broad while still making each project concrete and
testable. The repository favors small research-engineering labs over notebooks
that are hard to reproduce.

## Implemented Coverage

| Discipline | Lab | What It Demonstrates |
| --- | --- | --- |
| Agentic AI | `tool-trajectory-audit-lab` | Agent trace auditing, tool loop detection, recovery quality |
| Agentic AI | `agentic-ablation-benchmark` | Variant comparison across prompt, tool-policy, retrieval, cost, and recovery |
| Reinforcement Learning | `bandit-policy-evaluation-lab` | Offline policy evaluation, IPS/SNIPS, support diagnostics, regret alerts |
| Recommender Systems | `ranking-recommender-lab` | Ranking metrics, coverage diagnostics, long-tail exposure, cold-start analysis |
| LLM / RAG | `citation-grounding-lab` | Claim grounding, citation precision, contradiction checks |
| LLM / Context Engineering | `long-context-stress-lab` | Context packing, relevant coverage, answer drift |
| LLM Evaluation | `prompt-rubric-distillation-lab` | Rubric normalization, scorecard generation, ambiguity flags |
| LLM / Multi-Hop Reasoning | `multi-hop-evidence-mapper` | Hop support mapping, bridge continuity, conclusion grounding |
| Computer Vision | `vision-evaluation-lab` | Detection IoU, greedy matching, classification metrics |
| NLP | `nlp-semantic-evaluation-lab` | Text similarity, entity F1, intent accuracy |
| Machine Learning | `tabular-ml-reliability-lab` | Drift checks, missingness shifts, leakage candidates |
| Data Science | `time-series-forecasting-lab` | Rolling backtests, baseline forecasting, MAE and SMAPE |
| MLOps | `mlops-experiment-registry-lab` | Experiment ranking, promotion gates, reproducibility metadata |

## Expansion Backlog

| Future Discipline | Candidate Lab | Research Angle |
| --- | --- | --- |
| Multimodal AI | `multimodal-retrieval-lab` | Image/text retrieval, cross-modal ranking quality |
| Graph ML | `graph-representation-lab` | Link prediction splits, neighborhood leakage checks |
| Speech AI | `speech-transcription-eval-lab` | WER/CER, timestamp drift, noisy-audio slices |
| Responsible AI | `fairness-slice-audit-lab` | Group metrics, disparity alerts, model-card evidence |

## Quality Bar

- Each implemented lab should include executable source code and tests.
- Each lab should keep data assets small and auditable.
- Heavy frameworks can be added only when they materially improve the research signal.
- Docs should explain the evaluation design, not only list technologies.
