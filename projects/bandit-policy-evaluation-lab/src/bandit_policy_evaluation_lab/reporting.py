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
    policy_rows = "".join(
        (
            "<tr>"
            f"<td data-label=\"Policy\">{escape(evaluation.policy.policy_id)}</td>"
            f"<td data-label=\"Family\">{escape(evaluation.policy.family)}</td>"
            f"<td data-label=\"Explore\">{evaluation.policy.exploration_rate:.2f}</td>"
            f"<td data-label=\"Score\">{evaluation.overall_score:.2f}</td>"
            f"<td data-label=\"SNIPS\">{evaluation.snips_reward:.2f}</td>"
            f"<td data-label=\"Support\">{evaluation.support_rate:.0%}</td>"
            f"<td data-label=\"ESS\">{evaluation.effective_sample_ratio:.2f}</td>"
            f"<td data-label=\"Regret\">{evaluation.regret_estimate:.2f}</td>"
            "</tr>"
        )
        for evaluation in scenario_result.policy_evaluations
    )

    segment_rows = "".join(
        (
            "<tr>"
            f"<td data-label=\"Policy\">{escape(evaluation.policy.policy_id)}</td>"
            f"<td data-label=\"Segment\">{escape(segment.segment)}</td>"
            f"<td data-label=\"Events\">{segment.event_count}</td>"
            f"<td data-label=\"Support\">{segment.support_rate:.0%}</td>"
            f"<td data-label=\"SNIPS\">{segment.snips_reward:.2f}</td>"
            f"<td data-label=\"Regret\">{segment.regret_estimate:.2f}</td>"
            "</tr>"
        )
        for evaluation in scenario_result.policy_evaluations
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
        f"Mean Support={metrics.mean_support_rate:.0%} | Best Policy={metrics.best_policy_id}"
    )
    return (
        "<section class=\"scenario\">"
        f"<h2>{escape(scenario_result.scenario.scenario_id)}</h2>"
        f"<p><strong>Name:</strong> {escape(scenario_result.scenario.name)}</p>"
        f"<p class=\"scenario-summary\">{escape(summary)}</p>"
        "<h3>Policy Evaluations</h3>"
        "<table>"
        "<thead><tr><th>Policy</th><th>Family</th><th>Explore</th><th>Score</th><th>SNIPS</th><th>Support</th><th>ESS</th><th>Regret</th></tr></thead>"
        f"<tbody>{policy_rows}</tbody>"
        "</table>"
        "<h3>Segment Diagnostics</h3>"
        "<table>"
        "<thead><tr><th>Policy</th><th>Segment</th><th>Events</th><th>Support</th><th>SNIPS</th><th>Regret</th></tr></thead>"
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
            _metric_card("Policies", str(metrics.policy_count)),
            _metric_card("Mean SNIPS", f"{metrics.mean_snips_reward:.2f}"),
            _metric_card("Support", f"{metrics.mean_support_rate:.0%}"),
            _metric_card("ESS", f"{metrics.mean_effective_sample_ratio:.2f}"),
            _metric_card("Mean Regret", f"{metrics.mean_regret_estimate:.2f}"),
            _metric_card("Findings", str(metrics.total_findings)),
        ]
    )
    sections = "".join(_render_scenario(scenario_result) for scenario_result in result.scenarios)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Bandit Policy Evaluation Lab Report</title>
  <style>
    :root {{
      --bg: #f5f5ef;
      --panel: #ffffff;
      --ink: #19212c;
      --muted: #687380;
      --line: #d8dde5;
      --accent: #0f766e;
    }}
    body {{
      margin: 0;
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      color: var(--ink);
      background: radial-gradient(circle at top, #f6fff7 0%, var(--bg) 60%);
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
      box-shadow: 0 12px 30px rgba(25, 33, 44, 0.06);
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
      box-shadow: 0 12px 30px rgba(25, 33, 44, 0.06);
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
      <h1>Bandit Policy Evaluation Lab Report</h1>
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
