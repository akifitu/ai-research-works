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
    hop_rows: list[str] = []
    for hop in case_result.hop_evaluations:
        top_docs = ", ".join(score.doc_id for score in hop.doc_scores[:2]) or "none"
        hop_rows.append(
            "<tr>"
            f"<td data-label=\"Hop\">{escape(hop.hop.hop_id)}</td>"
            f"<td data-label=\"Claim\">{escape(hop.hop.claim)}</td>"
            f"<td data-label=\"Support\">{hop.support_score:.2f}</td>"
            f"<td data-label=\"Top Docs\">{escape(top_docs)}</td>"
            f"<td data-label=\"Bridge Terms\">{escape(', '.join(hop.hop.bridge_terms) or 'none')}</td>"
            "</tr>"
        )

    bridge_rows = "".join(
        (
            "<tr>"
            f"<td data-label=\"From\">{escape(bridge.from_hop_id)}</td>"
            f"<td data-label=\"To\">{escape(bridge.to_hop_id)}</td>"
            f"<td data-label=\"Shared Terms\">{escape(', '.join(bridge.shared_bridge_terms) or 'none')}</td>"
            f"<td data-label=\"Support\">{bridge.support_score:.2f}</td>"
            "</tr>"
        )
        for bridge in case_result.bridge_evaluations
    ) or "<tr><td colspan=\"4\">No bridge pairs</td></tr>"

    findings = "".join(
        (
            "<li>"
            f"<strong>{escape(finding.category)}</strong>: {escape(finding.description)}"
            "</li>"
        )
        for finding in case_result.findings
    ) or "<li>No findings</li>"

    metrics = case_result.metrics
    summary = (
        f"Hop Support={metrics.mean_hop_support:.0%} | Bridge Support={metrics.mean_bridge_support:.0%} | "
        f"Conclusion={metrics.conclusion_support:.0%} | Document Coverage={metrics.mapped_document_coverage:.0%}"
    )
    return (
        "<section class=\"case\">"
        f"<h2>{escape(case_result.case.case_id)}</h2>"
        f"<p><strong>Question:</strong> {escape(case_result.case.question)}</p>"
        f"<p><strong>Answer:</strong> {escape(case_result.case.answer)}</p>"
        f"<p class=\"case-summary\">{escape(summary)}</p>"
        "<h3>Hop Mapping</h3>"
        "<table>"
        "<thead><tr><th>Hop</th><th>Claim</th><th>Support</th><th>Top Docs</th><th>Bridge Terms</th></tr></thead>"
        f"<tbody>{''.join(hop_rows)}</tbody>"
        "</table>"
        "<h3>Bridge Checks</h3>"
        "<table>"
        "<thead><tr><th>From</th><th>To</th><th>Shared Terms</th><th>Support</th></tr></thead>"
        f"<tbody>{bridge_rows}</tbody>"
        "</table>"
        "<h3>Findings</h3>"
        f"<ul>{findings}</ul>"
        "</section>"
    )


def render_report(result: ExperimentResult) -> str:
    metrics = result.aggregate_metrics
    cards = "".join(
        [
            _metric_card("Cases", str(metrics.case_count)),
            _metric_card("Hops", str(metrics.total_hops)),
            _metric_card("Mean Hop Support", f"{metrics.mean_hop_support:.0%}"),
            _metric_card("Mean Bridge Support", f"{metrics.mean_bridge_support:.0%}"),
            _metric_card("Mean Conclusion", f"{metrics.mean_conclusion_support:.0%}"),
            _metric_card("Findings", str(metrics.total_findings)),
        ]
    )
    case_sections = "".join(_render_case(case_result) for case_result in result.cases)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Multi-Hop Evidence Mapper Report</title>
  <style>
    :root {{
      --bg: #f2f4ee;
      --panel: #ffffff;
      --ink: #17232d;
      --muted: #61707b;
      --line: #d8e0e5;
    }}
    body {{
      margin: 0;
      font-family: "Avenir Next", "Segoe UI", sans-serif;
      color: var(--ink);
      background: linear-gradient(180deg, #f9fff7 0%, var(--bg) 100%);
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
      box-shadow: 0 10px 28px rgba(23, 35, 45, 0.06);
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
      box-shadow: 0 10px 28px rgba(23, 35, 45, 0.06);
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
      <h1>Multi-Hop Evidence Mapper Report</h1>
      <p>{escape(result.benchmark_id)} | {escape(result.config.experiment_name)} | Generated {escape(result.generated_at)}</p>
      <p>{escape(result.benchmark_description)}</p>
    </header>
    <section class="metrics">{cards}</section>
    {case_sections}
  </main>
</body>
</html>
"""


def write_html_report(path: str | Path, result: ExperimentResult) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_report(result), encoding="utf-8")
