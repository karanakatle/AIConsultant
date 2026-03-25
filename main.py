#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from orchestrator import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local-first AI workflow analyzer")
    parser.add_argument("--input", required=True, help="Path to input file (.pdf/.txt/.md/.json)")
    parser.add_argument("--output", default="runs", help="Output run directory root")
    parser.add_argument(
        "--auto-fallback",
        action="store_true",
        help="Skip interactive LLM prompts and use deterministic fallback outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.auto_fallback:
        llm = lambda _prompt: "SKIP"
    else:
        llm = None

    run_dir = run_pipeline(Path(args.input), Path(args.output), llm=llm)
    print(f"✅ Report generated in: {run_dir}")


if __name__ == "__main__":
    main()
