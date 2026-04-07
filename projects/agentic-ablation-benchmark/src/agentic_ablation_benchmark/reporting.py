from __future__ import annotations

from html import escape
from pathlib import Path

from .models import ExperimentResult, TaskResult


def _metric_card(label: str, value: str) -> str:
    return (
        '<div class="metric-card">'
        f"<span class=\"metric-label\">{escape(label)}</span>"
        f"<strong>{escape(value)}</strong>"
        "</div>"
    )


def _render_task(task_result: TaskResult) -> str:
    rows: list[str] = []
    for score in task_result.scored_variants:
        rows.append(
            "<tr>"
            f"<td data-label=\"Variant\">{escape(score.variant.variant_id)}</td>"
            f"<td data-label=\"Prompt\">{escape(score.variant.prompt_strategy)}</td>"
            f"<td data-label=\"Tool\">{escape(score.variant.tool_policy)}</td>"
            f"<td data-label=\"Retrieval\">{escape(score.variant.retrieval_policy)}</td>"
            f"<td data-label=\"Complete\">{escape('yes' if score.variant.completed else 'no')}</td>"
            f"<td data-label=\"Score\">{score.overall_score:.2f}</td>"
            f"<td data-label=\"Recovery\">{score.recovery_score:.2f}</td>"
            f"<td data-label=\"Latency\">{score.latency_score:.2f}</td>"
            f"<td data-label=\"Tokens\">{score.total_tokens}</td>"
            "</tr>"
        )

    factor_rows = "".join(
        (
            "<tr>"
            f"<td data-label=\"Factor\">{escape(summary.factor_name)}</td>"
            f"<td data-label=\"Value\">{escape(summary.factor_value)}</td>"
            f"<td data-label=\"Comparisons\">{summary.comparison_count}</td>"
            f"<td data-label=\"Mean Delta\">{summary.mean_delta:.2f}</td>"
            f"<td data-label=\"Win Rate\">{summary.win_rate:.0%}</td>"
            "</tr>"
        )
        for summary in task_result.factor_summaries
    ) or "<tr><td colspan=\"5\">No factor deltas</td></tr>"

    findings = "".join(
        (
            "<li>"
            f"<strong>{escape(finding.category)}</strong>: {escape(finding.description)}"
            "</li>"
        )
        for finding in task_result.findings
    ) or "<li>No findings</li>"

    metrics = task_result.metrics
    summary = (
        f"Baseline={metrics.baseline_score:.0%} | Best={metrics.best_score:.0%} | "
        f"Completion={metrics.completion_rate:.0%} | Best Variant={metrics.best_variant_id}"
    )
    return (
        "<section class=\"task\">"
        f"<h2>{escape(task_result.task.task_id)}</h2>"
        f"<p><strong>Name:</strong> {escape(task_result.task.name)}</p>"
        f"<p class=\"task-summary\">{escape(summary)}</p>"
        "<h3>Variants</h3>"
        "<table>"
        "<thead><tr><th>Variant</th><th>Prompt</th><th>Tool</th><th>Retrieval</th><th>Complete</th><th>Score</th><th>Recovery</th><th>Latency</th><th>Tokens</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
        "<h3>Factor Summaries</h3>"
        "<table>"
        "<thead><tr><th>Factor</th><th>Value</th><th>Comparisons</th><th>Mean Delta</th><th>Win Rate</th></tr></thead>"
        f"<tbody>{factor_rows}</tbody>"
        "</table>"
        "<h3>Findings</h3>"
        f"<ul>{findings}</ul>"
        "</section>"
    )


def render_report(result: ExperimentResult) -> str:
    metrics = result.aggregate_metrics
    cards = "".join(
        [
            _metric_card("Tasks", str(metrics.task_count)),
            _metric_card("Variants", str(metrics.variant_count)),
            _metric_card("Completion", f"{metrics.mean_completion_rate:.0%}"),
            _metric_card("Mean Score", f"{metrics.mean_score:.0%}"),
            _metric_card("Recovery", f"{metrics.mean_recovery_score:.0%}"),
            _metric_card("Findings", str(metrics.total_findings)),
        ]
    )
    sections = "".join(_render_task(task_result) for task_result in result.tasks)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agentic Ablation Benchmark Report</title>
  <style>
    :root {{
      --bg: #f5f6f1;
      --panel: #ffffff;
      --ink: #162230;
      --muted: #64707a;
      --line: #d9e0e6;
    }}
    body {{
      margin: 0;
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      color: var(--ink);
      background: linear-gradient(180deg, #f7fff9 0%, var(--bg) 100%);
    }}
    main {{
      max-width: 1160px;
      margin: 0 auto;
      padding: 40px 20px 80px;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
      margin: 24px 0 32px;
    }}
    .metric-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 16px;
      box-shadow: 0 10px 28px rgba(22, 34, 48, 0.06);
    }}
    .metric-label {{
      display: block;
      color: var(--muted);
      font-size: 0.9rem;
      margin-bottom: 6px;
    }}
    .task {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 20px;
      margin-top: 24px;
      box-shadow: 0 10px 28px rgba(22, 34, 48, 0.06);
    }}
    .task-summary {{
      color: var(--muted);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 18px;
      font-size: 0.95rem;
    }}
    th, td {{
      border-top: 1px solid var(--line);
      padding: 12px 10px;
      vertical-align: top;
      text-align: left;
    }}
    th {{
      color: var(--muted);
      font-weight: 600;
    }}
    ul {{
      padding-left: 20px;
    }}
    @media (max-width: 900px) {{
      table, thead, tbody, th, td, tr {{
        display: block;
      }}
      thead {{
        display: none;
      }}
      td {{
        padding: 10px 0;
      }}
      td::before {{
        content: attr(data-label);
        display: block;
        font-size: 0.8rem;
        color: var(--muted);
        margin-bottom: 4px;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Agentic Ablation Benchmark Report</h1>
      <p>{escape(result.benchmark_id)} | {escape(result.config.experiment_name)} | Generated {escape(result.generated_at)}</p>
      <p>{escape(result.benchmark_description)}</p>
    </header>
    <section class="metrics">{cards}</section>
    {sections}
  </main>
</body>
</html>
"""


def write_html_report(path: str | Path, result: ExperimentResult) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_report(result), encoding="utf-8")

