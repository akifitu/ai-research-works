from __future__ import annotations

import argparse
import json
from pathlib import Path

from .dataset import load_benchmark, load_config
from .reporting import result_to_dict
from .runner import TabularReliabilityRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a tabular ML reliability audit.")
    parser.add_argument("--benchmark", required=True, type=Path)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "configs" / "default_reliability.json",
    )
    parser.add_argument("--output", type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = TabularReliabilityRunner(load_config(args.config)).run_benchmark(
        load_benchmark(args.benchmark)
    )
    payload = json.dumps(result_to_dict(result), indent=2)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
