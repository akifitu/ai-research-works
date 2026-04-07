from __future__ import annotations

from html import escape
from pathlib import Path

from .models import ExperimentResult, RunResult


def _metric_card(label: str, value: str) -> str:
    return (
        '<div class="metric-card">'
        f"<span class=\"metric-label\">{escape(label)}</span>"
        f"<strong>{escape(value)}</strong>"
        "</div>"
    )


def _render_run(run_result: RunResult) -> str:
    finding_rows: list[str] = []
    for finding in run_result.findings:
        finding_rows.append(
            "<tr>"
            f"<td data-label=\"Finding\">{escape(finding.finding_id)}</td>"
            f"<td data-label=\"Category\"><span class=\"chip chip-{finding.category.lower()}\">{escape(finding.category)}</span></td>"
            f"<td data-label=\"Severity\">{escape(finding.severity)}</td>"
            f"<td data-label=\"Steps\">{escape(', '.join(finding.step_ids))}</td>"
            f"<td data-label=\"Title\">{escape(finding.title)}</td>"
            f"<td data-label=\"Description\">{escape(finding.description)}</td>"
            "</tr>"
        )

    metrics = run_result.metrics
    metric_line = (
        f"Failures={metrics.failure_count} | Recovered={metrics.recovered_failure_count} | "
        f"Loops={metrics.loop_count} | Redundancy={metrics.redundancy_rate:.0%} | "
        f"Efficiency={metrics.efficiency_score:.0%}"
    )
    return (
        "<section class=\"run\">"
        f"<h2>{escape(run_result.run.run_id)}</h2>"
        f"<p><strong>Task:</strong> {escape(run_result.run.task)}</p>"
        f"<p class=\"run-metrics\">{escape(metric_line)}</p>"
        "<table>"
        "<thead>"
        "<tr>"
        "<th>Finding</th>"
        "<th>Category</th>"
        "<th>Severity</th>"
        "<th>Steps</th>"
        "<th>Title</th>"
        "<th>Description</th>"
        "</tr>"
        "</thead>"
        f"<tbody>{''.join(finding_rows) or '<tr><td colspan=\"6\">No findings</td></tr>'}</tbody>"
        "</table>"
        "</section>"
    )


def render_report(result: ExperimentResult) -> str:
    metrics = result.aggregate_metrics
    cards = "".join(
        [
            _metric_card("Runs", str(metrics.run_count)),
            _metric_card("Failures", str(metrics.total_failures)),
            _metric_card("Loops", str(metrics.total_loops)),
            _metric_card("Empty Results", str(metrics.total_empty_result_findings)),
            _metric_card("Mean Recovery", f"{metrics.mean_recovery_rate:.0%}"),
            _metric_card("Mean Efficiency", f"{metrics.mean_efficiency_score:.0%}"),
        ]
    )
    runs_html = "".join(_render_run(run_result) for run_result in result.runs)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tool Trajectory Audit Report</title>
  <style>
    :root {{
      --bg: #f4f4ef;
      --panel: #ffffff;
      --ink: #18222f;
      --muted: #5f6870;
      --line: #d5dde4;
      --loop: #9a3412;
      --failure: #b91c1c;
      --recovery: #0f766e;
      --empty: #475569;
      --latency: #1d4ed8;
    }}
    body {{
      margin: 0;
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      background: radial-gradient(circle at top left, #fff7ed 0%, var(--bg) 46%);
      color: var(--ink);
    }}
    main {{
      max-width: 1120px;
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
      box-shadow: 0 10px 30px rgba(24, 34, 47, 0.06);
    }}
    .metric-label {{
      display: block;
      color: var(--muted);
      font-size: 0.9rem;
      margin-bottom: 6px;
    }}
    .run {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 20px;
      margin-top: 24px;
      box-shadow: 0 10px 30px rgba(24, 34, 47, 0.06);
    }}
    .run-metrics {{
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
    .chip {{
      display: inline-block;
      border-radius: 999px;
      padding: 4px 10px;
      color: white;
      font-size: 0.82rem;
      letter-spacing: 0.02em;
    }}
    .chip-loop {{
      background: var(--loop);
    }}
    .chip-failure {{
      background: var(--failure);
    }}
    .chip-recovery {{
      background: var(--recovery);
    }}
    .chip-empty_result {{
      background: var(--empty);
    }}
    .chip-latency {{
      background: var(--latency);
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
      <h1>Tool Trajectory Audit Report</h1>
      <p>{escape(result.benchmark_id)} | {escape(result.config.experiment_name)} | Generated {escape(result.generated_at)}</p>
      <p>{escape(result.benchmark_description)}</p>
    </header>
    <section class="metrics">{cards}</section>
    {runs_html}
  </main>
</body>
</html>
"""


def write_html_report(path: str | Path, result: ExperimentResult) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_report(result), encoding="utf-8")
