from __future__ import annotations

from html import escape
from pathlib import Path

from .models import CaseResult, ExperimentResult


def _metric_card(label: str, value: str) -> str:
    return (
        '<div class="metric-card">'
        f"<span class=\"metric-label\">{escape(label)}</span>"
        f"<strong>{escape(value)}</strong>"
        "</div>"
    )


def _render_case(case_result: CaseResult) -> str:
    rows: list[str] = []
    for evaluation in case_result.evaluations:
        categories = ", ".join(finding.category for finding in evaluation.findings) or "none"
        rows.append(
            "<tr>"
            f"<td data-label=\"Snapshot\">{escape(evaluation.snapshot.snapshot_id)}</td>"
            f"<td data-label=\"Budget\">{evaluation.snapshot.budget_tokens}</td>"
            f"<td data-label=\"Packed\">{escape(', '.join(evaluation.packed_context_ids) or 'none')}</td>"
            f"<td data-label=\"Coverage\">{evaluation.relevant_coverage:.2f}</td>"
            f"<td data-label=\"Noise\">{evaluation.noise_ratio:.2f}</td>"
            f"<td data-label=\"Align\">{evaluation.reference_alignment:.2f}</td>"
            f"<td data-label=\"Support\">{evaluation.answer_support:.2f}</td>"
            f"<td data-label=\"Unsupported\">{evaluation.unsupported_token_rate:.2f}</td>"
            f"<td data-label=\"Drift\">{evaluation.drift_score:.2f}</td>"
            f"<td data-label=\"Findings\">{escape(categories)}</td>"
            "</tr>"
        )

    metrics = case_result.metrics
    summary = (
        f"Snapshots={metrics.snapshot_count} | Coverage={metrics.mean_relevant_coverage:.0%} | "
        f"Noise={metrics.mean_noise_ratio:.0%} | Alignment={metrics.mean_reference_alignment:.0%} | "
        f"Max Drift={metrics.max_drift_score:.0%}"
    )
    finding_blocks = "".join(
        (
            "<li>"
            f"<strong>{escape(finding.category)}</strong>: {escape(finding.description)}"
            "</li>"
        )
        for evaluation in case_result.evaluations
        for finding in evaluation.findings
    ) or "<li>No findings</li>"
    return (
        "<section class=\"case\">"
        f"<h2>{escape(case_result.case.case_id)}</h2>"
        f"<p><strong>Question:</strong> {escape(case_result.case.question)}</p>"
        f"<p><strong>Reference:</strong> {escape(case_result.case.reference_answer)}</p>"
        f"<p class=\"case-summary\">{escape(summary)}</p>"
        "<table>"
        "<thead>"
        "<tr>"
        "<th>Snapshot</th>"
        "<th>Budget</th>"
        "<th>Packed Context</th>"
        "<th>Coverage</th>"
        "<th>Noise</th>"
        "<th>Alignment</th>"
        "<th>Support</th>"
        "<th>Unsupported</th>"
        "<th>Drift</th>"
        "<th>Findings</th>"
        "</tr>"
        "</thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
        "<h3>Findings</h3>"
        f"<ul>{finding_blocks}</ul>"
        "</section>"
    )


def render_report(result: ExperimentResult) -> str:
    metrics = result.aggregate_metrics
    metric_cards = "".join(
        [
            _metric_card("Cases", str(metrics.case_count)),
            _metric_card("Snapshots", str(metrics.snapshot_count)),
            _metric_card("Mean Coverage", f"{metrics.mean_relevant_coverage:.0%}"),
            _metric_card("Mean Noise", f"{metrics.mean_noise_ratio:.0%}"),
            _metric_card("Mean Alignment", f"{metrics.mean_reference_alignment:.0%}"),
            _metric_card("Max Drift", f"{metrics.max_drift_score:.0%}"),
        ]
    )
    cases_html = "".join(_render_case(case_result) for case_result in result.cases)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Long Context Stress Report</title>
  <style>
    :root {{
      --bg: #f7f2eb;
      --panel: #ffffff;
      --ink: #1b2430;
      --muted: #626d79;
      --line: #d8dee5;
    }}
    body {{
      margin: 0;
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      color: var(--ink);
      background: linear-gradient(180deg, #fff8ef 0%, var(--bg) 100%);
    }}
    main {{
      max-width: 1140px;
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
      box-shadow: 0 10px 28px rgba(27, 36, 48, 0.06);
    }}
    .metric-label {{
      display: block;
      color: var(--muted);
      font-size: 0.9rem;
      margin-bottom: 6px;
    }}
    .case {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 20px;
      margin-top: 24px;
      box-shadow: 0 10px 28px rgba(27, 36, 48, 0.06);
    }}
    .case-summary {{
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
      <h1>Long Context Stress Report</h1>
      <p>{escape(result.benchmark_id)} | {escape(result.config.experiment_name)} | Generated {escape(result.generated_at)}</p>
      <p>{escape(result.benchmark_description)}</p>
    </header>
    <section class="metrics">{metric_cards}</section>
    {cases_html}
  </main>
</body>
</html>
"""


def write_html_report(path: str | Path, result: ExperimentResult) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_report(result), encoding="utf-8")
