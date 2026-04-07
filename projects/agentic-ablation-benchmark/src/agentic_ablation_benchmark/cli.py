from __future__ import annotations

import argparse
from pathlib import Path

from .dataset import load_benchmark, load_config, write_experiment_result
from .reporting import write_html_report
from .runner import ExperimentRunner


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run an agentic ablation benchmark on prerecorded task variants."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run agentic ablation benchmark")
    run_parser.add_argument("--benchmark", required=True, help="Path to benchmark JSON")
    run_parser.add_argument("--config", required=True, help="Path to config JSON")
    run_parser.add_argument("--output-dir", required=True, help="Directory for outputs")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command != "run":
        parser.error(f"Unsupported command: {args.command}")

    benchmark = load_benchmark(args.benchmark)
    config = load_config(args.config)
    result = ExperimentRunner(config).run_benchmark(benchmark)

    output_dir = Path(args.output_dir)
    write_experiment_result(output_dir / "results.json", result)
    write_html_report(output_dir / "report.html", result)

    print(f"Wrote results to {output_dir / 'results.json'}")
    print(f"Wrote HTML report to {output_dir / 'report.html'}")
    return 0

