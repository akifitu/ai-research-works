from __future__ import annotations

from html import escape
from pathlib import Path

from .models import ExperimentResult, RubricResult


def _metric_card(label: str, value: str) -> str:
    return (
        '<div class="metric-card">'
        f"<span class=\"metric-label\">{escape(label)}</span>"
        f"<strong>{escape(value)}</strong>"
        "</div>"
    )


def _render_rubric(rubric_result: RubricResult) -> str:
    rows: list[str] = []
    for criterion in rubric_result.distilled_criteria:
        rows.append(
            "<tr>"
            f"<td data-label=\"Criterion\">{escape(criterion.criterion_id)}</td>"
            f"<td data-label=\"Dimension\">{escape(criterion.dimension)}</td>"
            f"<td data-label=\"Scale\">{escape(criterion.scale_type)}</td>"
            f"<td data-label=\"Weight\">{criterion.normalized_weight:.2f}</td>"
            f"<td data-label=\"Ambiguity\">{escape(', '.join(criterion.ambiguity_flags) or 'none')}</td>"
            f"<td data-label=\"Specificity\">{criterion.specificity_score:.2f}</td>"
            f"<td data-label=\"Checklist\">{escape(' | '.join(criterion.checklist_questions))}</td>"
            "</tr>"
        )

    findings = "".join(
        (
            "<li>"
            f"<strong>{escape(finding.category)}</strong>: {escape(finding.description)}"
            "</li>"
        )
        for finding in rubric_result.findings
    ) or "<li>No findings</li>"
    metrics = rubric_result.metrics
    summary = (
        f"Criteria={metrics.criterion_count} | Ambiguity={metrics.ambiguity_rate:.0%} | "
        f"Specificity={metrics.mean_specificity_score:.0%} | "
        f"Explicit Weights={metrics.explicit_weight_coverage:.0%}"
    )
    return (
        "<section class=\"rubric\">"
        f"<h2>{escape(rubric_result.rubric.rubric_id)}</h2>"
        f"<p><strong>Task:</strong> {escape(rubric_result.rubric.task)}</p>"
        f"<p class=\"rubric-summary\">{escape(summary)}</p>"
        "<table>"
        "<thead>"
        "<tr>"
        "<th>Criterion</th>"
        "<th>Dimension</th>"
        "<th>Scale</th>"
        "<th>Weight</th>"
        "<th>Ambiguity</th>"
        "<th>Specificity</th>"
        "<th>Checklist</th>"
        "</tr>"
        "</thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
        "<h3>Findings</h3>"
        f"<ul>{findings}</ul>"
        "</section>"
    )


def render_report(result: ExperimentResult) -> str:
    metrics = result.aggregate_metrics
    cards = "".join(
        [
            _metric_card("Rubrics", str(metrics.rubric_count)),
            _metric_card("Criteria", str(metrics.total_criteria)),
            _metric_card("Mean Ambiguity", f"{metrics.mean_ambiguity_rate:.0%}"),
            _metric_card("Mean Specificity", f"{metrics.mean_specificity_score:.0%}"),
            _metric_card("Weight Coverage", f"{metrics.mean_explicit_weight_coverage:.0%}"),
            _metric_card("Findings", str(metrics.total_findings)),
        ]
    )
    rubric_sections = "".join(_render_rubric(rubric_result) for rubric_result in result.rubrics)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Prompt Rubric Distillation Report</title>
  <style>
    :root {{
      --bg: #f5f0ec;
      --panel: #ffffff;
      --ink: #1b2530;
      --muted: #64707b;
      --line: #d8dfe7;
    }}
    body {{
      margin: 0;
      font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
      color: var(--ink);
      background: linear-gradient(180deg, #fff8f4 0%, var(--bg) 100%);
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
      box-shadow: 0 10px 28px rgba(27, 37, 48, 0.06);
    }}
    .metric-label {{
      display: block;
      color: var(--muted);
      font-size: 0.9rem;
      margin-bottom: 6px;
    }}
    .rubric {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 20px;
      margin-top: 24px;
      box-shadow: 0 10px 28px rgba(27, 37, 48, 0.06);
    }}
    .rubric-summary {{
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
      <h1>Prompt Rubric Distillation Report</h1>
      <p>{escape(result.benchmark_id)} | {escape(result.config.experiment_name)} | Generated {escape(result.generated_at)}</p>
      <p>{escape(result.benchmark_description)}</p>
    </header>
    <section class="metrics">{cards}</section>
    {rubric_sections}
  </main>
</body>
</html>
"""


def write_html_report(path: str | Path, result: ExperimentResult) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_report(result), encoding="utf-8")
