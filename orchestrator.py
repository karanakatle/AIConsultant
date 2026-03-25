from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from agents.extractor import run_extractor
from agents.flow_builder import build_flow
from agents.optimizer import propose_agents
from agents.report import generate_report
from agents.roi import calculate_roi
from agents.understanding import analyze_flow
from utils.chunking import chunk_text


def _heuristic_confidence(line: str) -> float:
    score = 0.72
    if len(line.split()) >= 5:
        score += 0.08
    if re.search(r"\d", line):
        score += 0.06
    if any(x in line for x in ["->", ":", "%"]):
        score += 0.06
    if "???" in line.lower() or "illegible" in line.lower():
        score -= 0.35
    return max(0.0, min(0.99, round(score, 2)))


def _fallback_flow(raw_text: str) -> str:
    lines = [ln.strip(" -•") for ln in raw_text.splitlines() if ln.strip()]
    if not lines:
        return "flowchart TD\n    A[No content extracted]"

    steps = lines[:20]
    out = ["flowchart TD"]
    for i, step in enumerate(steps, start=1):
        label = step.replace('"', "'")
        out.append(f'    N{i}["S{i:02d} {label}"]')
        if i > 1:
            out.append(f"    N{i-1} --> N{i}")
    return "\n".join(out)


def _manual_llm(prompt: str) -> str:
    print("\n=== COPY INTO COPILOT/LLM ===\n")
    print(prompt)
    print("\n=== END PROMPT ===\n")
    return input("Paste model response (or type SKIP for fallback):\n").strip()


def run_pipeline(file_path: Path, output_root: Path, llm: Callable[[str], str] | None = None) -> Path:
    llm = llm or _manual_llm

    extracted = run_extractor(file_path)
    text = extracted["text"]
    chunks = chunk_text(text)

    flow = build_flow(llm, chunks)
    if not flow or flow.upper() == "SKIP":
        flow = _fallback_flow(text)

    analysis = analyze_flow(llm, flow)
    if not analysis or analysis.upper() == "SKIP":
        analysis = "Fallback analysis: manual intervention and duplicate checks likely where repetitive steps appear."

    proposals = propose_agents(llm, analysis)
    if not proposals or proposals.upper() == "SKIP":
        proposals = (
            "1) Easy/high ROI/low risk: exception summarization assistant\n"
            "2) Hard/high ROI/low risk: cross-queue balancing recommender\n"
            "3) Very risky: autonomous posting/decisioning"
        )

    roi = calculate_roi(llm, proposals)
    if not roi or roi.upper() == "SKIP":
        roi = (
            "Assumptions: 100k items/day, 4% exceptions, 25% handling-time reduction. "
            "Annual net benefit approx $492k at $120k run-cost."
        )

    report = generate_report(llm, flow, analysis, proposals, roi)
    if not report or report.upper() == "SKIP":
        report = (
            "# Executive Summary\n"
            "Fallback report generated due to manual SKIP choices.\n\n"
            "## Current Workflow\n" + flow + "\n\n"
            "## Key Issues\n" + analysis + "\n\n"
            "## Proposals\n" + proposals + "\n\n"
            "## ROI\n" + roi
        )

    raw_lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    low_conf = [
        {"line": ln, "confidence": _heuristic_confidence(ln)}
        for ln in raw_lines
        if _heuristic_confidence(ln) < 0.80
    ]

    run_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = output_root / run_ts
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "report.md").write_text(report, encoding="utf-8")
    (run_dir / "extracted_text.txt").write_text(text, encoding="utf-8")
    (run_dir / "flow_mermaid.mmd").write_text(flow, encoding="utf-8")
    (run_dir / "low_confidence.json").write_text(json.dumps(low_conf, indent=2), encoding="utf-8")
    (run_dir / "pipeline_state.json").write_text(
        json.dumps(
            {
                "input": str(file_path),
                "source": extracted.get("source"),
                "ocr_low_conf_tokens": extracted.get("low_conf", []),
                "low_conf_lines": low_conf,
                "analysis": analysis,
                "proposals": proposals,
                "roi": roi,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    return run_dir
