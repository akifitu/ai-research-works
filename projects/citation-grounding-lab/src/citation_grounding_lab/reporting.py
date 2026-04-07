from __future__ import annotations

from html import escape
from pathlib import Path

from .models import ExperimentResult, SampleResult


def _metric_card(label: str, value: str) -> str:
    return (
        '<div class="metric-card">'
        f"<span class=\"metric-label\">{escape(label)}</span>"
        f"<strong>{escape(value)}</strong>"
        "</div>"
    )


def _render_sample(sample_result: SampleResult) -> str:
    rows: list[str] = []
    for assessment in sample_result.assessments:
        evidence_summary = "<br>".join(
            escape(
                f"{chunk.rank}. {chunk.doc_id} ({chunk.score:.2f}) - {chunk.text[:120]}"
                + ("..." if len(chunk.text) > 120 else "")
            )
            for chunk in assessment.evidence[:3]
        ) or "No evidence"
        rows.append(
            "<tr>"
            f"<td data-label=\"Claim\">{escape(assessment.claim.claim_id)}</td>"
            f"<td data-label=\"Label\"><span class=\"label label-{assessment.label.lower()}\">{escape(assessment.label)}</span></td>"
            f"<td data-label=\"Support\">{assessment.support_score:.2f}</td>"
            f"<td data-label=\"Cited Docs\">{escape(', '.join(assessment.claim.cited_doc_ids) or 'none')}</td>"
            f"<td data-label=\"Matched Docs\">{escape(', '.join(assessment.matched_doc_ids) or 'none')}</td>"
            f"<td data-label=\"Top Evidence\">{evidence_summary}</td>"
            f"<td data-label=\"Rationale\">{escape(assessment.rationale)}</td>"
            "</tr>"
        )

    metrics = sample_result.metrics
    metrics_line = (
        f"Claims={metrics.claim_count} | Support Rate={metrics.support_rate:.0%} | "
        f"Citation Precision={metrics.citation_precision:.0%} | "
        f"Faithfulness={metrics.faithfulness_score:.0%}"
    )
    return (
        "<section class=\"sample\">"
        f"<h2>{escape(sample_result.sample.sample_id)}</h2>"
        f"<p><strong>Question:</strong> {escape(sample_result.sample.question)}</p>"
        f"<p><strong>Answer:</strong> {escape(sample_result.sample.answer)}</p>"
        f"<p class=\"sample-metrics\">{escape(metrics_line)}</p>"
        "<table>"
        "<thead>"
        "<tr>"
        "<th>Claim</th>"
        "<th>Label</th>"
        "<th>Support</th>"
        "<th>Cited Docs</th>"
        "<th>Matched Docs</th>"
        "<th>Top Evidence</th>"
        "<th>Rationale</th>"
        "</tr>"
        "</thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
        "</section>"
    )


def render_report(result: ExperimentResult) -> str:
    metrics = result.aggregate_metrics
    metric_cards = "".join(
        [
            _metric_card("Claims", str(metrics.claim_count)),
            _metric_card("Support Rate", f"{metrics.support_rate:.0%}"),
            _metric_card("Citation Precision", f"{metrics.citation_precision:.0%}"),
            _metric_card("Contradiction Rate", f"{metrics.contradiction_rate:.0%}"),
            _metric_card("Faithfulness", f"{metrics.faithfulness_score:.0%}"),
        ]
    )
    samples_html = "".join(_render_sample(sample_result) for sample_result in result.samples)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Citation Grounding Report</title>
  <style>
    :root {{
      --bg: #f6f7f2;
      --panel: #ffffff;
      --ink: #16212c;
      --muted: #5f6b76;
      --line: #d8e0e5;
      --accent: #0f766e;
      --supported: #0f766e;
      --partial: #b45309;
      --unsupported: #334155;
      --contradicted: #b91c1c;
    }}
    body {{
      margin: 0;
      font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", serif;
      background: linear-gradient(180deg, #eef2ea 0%, var(--bg) 100%);
      color: var(--ink);
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 40px 20px 80px;
    }}
    header {{
      margin-bottom: 24px;
    }}
    h1, h2 {{
      margin-bottom: 8px;
    }}
    p {{
      line-height: 1.6;
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
      box-shadow: 0 10px 30px rgba(22, 33, 44, 0.05);
    }}
    .metric-label {{
      display: block;
      color: var(--muted);
      font-size: 0.9rem;
      margin-bottom: 6px;
    }}
    .sample {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 20px;
      margin-top: 24px;
      box-shadow: 0 10px 30px rgba(22, 33, 44, 0.05);
    }}
    .sample-metrics {{
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
    .label {{
      display: inline-block;
      border-radius: 999px;
      padding: 4px 10px;
      color: white;
      font-size: 0.82rem;
      letter-spacing: 0.02em;
    }}
    .label-supported {{
      background: var(--supported);
    }}
    .label-partial {{
      background: var(--partial);
    }}
    .label-unsupported {{
      background: var(--unsupported);
    }}
    .label-contradicted {{
      background: var(--contradicted);
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
      <h1>Citation Grounding Lab Report</h1>
      <p>{escape(result.benchmark_id)} | {escape(result.config.experiment_name)} | Generated {escape(result.generated_at)}</p>
      <p>{escape(result.benchmark_description)}</p>
    </header>
    <section class="metrics">{metric_cards}</section>
    {samples_html}
  </main>
</body>
</html>
"""


def write_html_report(path: str | Path, result: ExperimentResult) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_report(result), encoding="utf-8")
