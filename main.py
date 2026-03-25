#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from orchestrator import run_pipeline


def llm(prompt: str) -> str:
    print("\n================ PROMPT ================\n")
    print(prompt)
    print("\n=======================================\n")
    return input("👉 Paste LLM response here:\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Workflow Analyzer")
    parser.add_argument("--file", required=True, help="Path to input PDF/text/json")
    parser.add_argument("--out", default="report.txt", help="Output report file path")
    parser.add_argument("--runs", default="runs", help="Run artifacts root directory")
    parser.add_argument("--auto-fallback", action="store_true", help="Skip manual LLM prompts")
    args = parser.parse_args()

    selected_llm = (lambda _p: "SKIP") if args.auto_fallback else llm
    result = run_pipeline(args.file, llm=selected_llm, output_root=args.runs)

    report_path = Path(result["run_dir"]) / "report.md"
    content = report_path.read_text(encoding="utf-8")
    Path(args.out).write_text(content, encoding="utf-8")

    print(f"\n✅ Report generated at: {args.out}")
    print(f"✅ Run artifacts folder: {result['run_dir']}")
    if result.get("winner"):
        print(f"✅ Top recommendation: {result['winner'].get('name')} (score: {result['winner'].get('final_score')})")


if __name__ == "__main__":
    main()
