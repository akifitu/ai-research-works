from __future__ import annotations

from html import escape
from pathlib import Path

from .models import ExperimentResult, ScenarioResult


def _metric_card(label: str, value: str) -> str:
    return (
        '<div class="metric-card">'
        f"<span class=\"metric-label\">{escape(label)}</span>"
        f"<strong>{escape(value)}</strong>"
        "</div>"
    )


def _render_scenario(scenario_result: ScenarioResult) -> str:
    system_rows = "".join(
        (
            "<tr>"
            f"<td data-label=\"System\">{escape(evaluation.system.system_id)}</td>"
            f"<td data-label=\"Family\">{escape(evaluation.system.family)}</td>"
            f"<td data-label=\"Score\">{evaluation.overall_score:.2f}</td>"
            f"<td data-label=\"NDCG@K\">{evaluation.ndcg_at_k:.2f}</td>"
            f"<td data-label=\"MAP@K\">{evaluation.map_at_k:.2f}</td>"
            f"<td data-label=\"Hit Rate\">{evaluation.hit_rate:.0%}</td>"
            f"<td data-label=\"Coverage\">{evaluation.coverage:.0%}</td>"
            f"<td data-label=\"Long Tail\">{evaluation.long_tail_share:.0%}</td>"
            "</tr>"
        )
        for evaluation in scenario_result.system_evaluations
    )

    segment_rows = "".join(
        (
            "<tr>"
            f"<td data-label=\"System\">{escape(evaluation.system.system_id)}</td>"
            f"<td data-label=\"Segment\">{escape(segment.segment)}</td>"
            f"<td data-label=\"Queries\">{segment.query_count}</td>"
            f"<td data-label=\"NDCG@K\">{segment.ndcg_at_k:.2f}</td>"
            f"<td data-label=\"MAP@K\">{segment.map_at_k:.2f}</td>"
            f"<td data-label=\"Hit Rate\">{segment.hit_rate:.0%}</td>"
            f"<td data-label=\"Long Tail\">{segment.long_tail_share:.0%}</td>"
            "</tr>"
        )
        for evaluation in scenario_result.system_evaluations
        for segment in evaluation.segment_summaries
    )

    findings = "".join(
        (
            "<li>"
            f"<strong>{escape(finding.category)}</strong>: {escape(finding.description)}"
            "</li>"
        )
        for finding in scenario_result.findings
    ) or "<li>No findings</li>"

    metrics = scenario_result.metrics
    summary = (
        f"Baseline={metrics.baseline_score:.2f} | Best={metrics.best_score:.2f} | "
        f"Mean NDCG={metrics.mean_ndcg_at_k:.2f} | Best System={metrics.best_system_id}"
    )
    return (
        "<section class=\"scenario\">"
        f"<h2>{escape(scenario_result.scenario.scenario_id)}</h2>"
        f"<p><strong>Name:</strong> {escape(scenario_result.scenario.name)}</p>"
        f"<p class=\"scenario-summary\">{escape(summary)}</p>"
        "<h3>System Evaluations</h3>"
        "<table>"
        "<thead><tr><th>System</th><th>Family</th><th>Score</th><th>NDCG@K</th><th>MAP@K</th><th>Hit Rate</th><th>Coverage</th><th>Long Tail</th></tr></thead>"
        f"<tbody>{system_rows}</tbody>"
        "</table>"
        "<h3>Segment Diagnostics</h3>"
        "<table>"
        "<thead><tr><th>System</th><th>Segment</th><th>Queries</th><th>NDCG@K</th><th>MAP@K</th><th>Hit Rate</th><th>Long Tail</th></tr></thead>"
        f"<tbody>{segment_rows}</tbody>"
        "</table>"
        "<h3>Findings</h3>"
        f"<ul>{findings}</ul>"
        "</section>"
    )


def render_report(result: ExperimentResult) -> str:
    metrics = result.aggregate_metrics
    cards = "".join(
        [
            _metric_card("Scenarios", str(metrics.scenario_count)),
            _metric_card("Systems", str(metrics.system_count)),
            _metric_card("Mean NDCG@K", f"{metrics.mean_ndcg_at_k:.2f}"),
            _metric_card("Mean MAP@K", f"{metrics.mean_map_at_k:.2f}"),
            _metric_card("Coverage", f"{metrics.mean_coverage:.0%}"),
            _metric_card("Long Tail", f"{metrics.mean_long_tail_share:.0%}"),
            _metric_card("Findings", str(metrics.total_findings)),
        ]
    )
    sections = "".join(_render_scenario(scenario_result) for scenario_result in result.scenarios)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Ranking Recommender Lab Report</title>
  <style>
    :root {{
      --bg: #f8f5ef;
      --panel: #ffffff;
      --ink: #1a2027;
      --muted: #697481;
      --line: #d8dde3;
      --accent: #b45309;
    }}
    body {{
      margin: 0;
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      color: var(--ink);
      background: radial-gradient(circle at top, #fff8ec 0%, var(--bg) 60%);
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
      box-shadow: 0 12px 30px rgba(26, 32, 39, 0.06);
    }}
    .metric-label {{
      display: block;
      color: var(--muted);
      font-size: 0.9rem;
      margin-bottom: 6px;
    }}
    .scenario {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 20px;
      margin-top: 24px;
      box-shadow: 0 12px 30px rgba(26, 32, 39, 0.06);
    }}
    .scenario-summary {{
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
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-weight: 600;
    }}
    ul {{
      padding-left: 20px;
    }}
    a {{
      color: var(--accent);
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
      <h1>Ranking Recommender Lab Report</h1>
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
