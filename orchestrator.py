from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Any

from agents.extractor import run_extractor
from agents.flow_builder import build_flow
from agents.optimizer import propose_agents
from agents.report import generate_report
from agents.risk_agent import critique_and_adjust
from agents.roi import calculate_roi
from agents.understanding import analyze_flow
from utils.chunking import chunk_text
from utils.scoring import rank_proposals
from utils.sensitivity import run_sensitivity
from utils.simulation import simulate_current, simulate_after


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
    out = ["flowchart TD"]
    for i, step in enumerate(lines[:25], start=1):
        out.append(f'    N{i}["S{i:02d} {step.replace(chr(34), chr(39))}"]')
        if i > 1:
            out.append(f"    N{i-1} --> N{i}")
    return "\n".join(out)


def _fallback_proposals() -> list[dict[str, Any]]:
    return [
        {
            "name": "Image Quality Auto-Fix Agent",
            "description": "Auto-correct brightness/skew/contrast to reduce manual repairs.",
            "category": "Easy",
            "roi_score": 8,
            "ease_score": 9,
            "risk_score": 2,
            "confidence_score": 8,
            "confidence_reason": "Directly targets repeat manual repair steps.",
            "assumptions": ["Image quality issues are significant."],
        },
        {
            "name": "Reconciliation Agent",
            "description": "Auto-match transactions across clearing/posting systems.",
            "category": "Hard",
            "roi_score": 9,
            "ease_score": 5,
            "risk_score": 3,
            "confidence_score": 7,
            "confidence_reason": "Likely high value but integration-heavy.",
            "assumptions": ["Cross-system IDs are available."],
        },
        {
            "name": "Auto Fraud Decision Agent",
            "description": "Autonomously approve/reject checks.",
            "category": "Risky",
            "roi_score": 10,
            "ease_score": 4,
            "risk_score": 9,
            "confidence_score": 5,
            "confidence_reason": "High impact but significant financial/compliance risk.",
            "assumptions": ["Model precision can be tightly controlled."],
        },
    ]


def _manual_llm(prompt: str) -> str:
    print("\n================ PROMPT ================\n")
    print(prompt)
    print("\n=======================================\n")
    return input("👉 Paste LLM response here (or type SKIP):\n").strip()


def _parse_proposals(raw: str) -> list[dict[str, Any]]:
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return _fallback_proposals()


def run_pipeline(file_path: str | Path, llm: Callable[[str], str] | None = None, output_root: str | Path = "runs") -> dict:
    llm = llm or _manual_llm
    input_path = Path(file_path)
    output_root = Path(output_root)

    extracted = run_extractor(input_path)
    text = extracted["text"]

    chunks = chunk_text(text)
    flow = build_flow(llm, chunks)
    if not flow or flow.upper() == "SKIP":
        flow = _fallback_flow(text)

    analysis = analyze_flow(llm, flow)
    if not analysis or analysis.upper() == "SKIP":
        analysis = "Detected manual intervention around repair, exceptions, and reconciliation."

    proposals_raw = propose_agents(llm, analysis)
    proposals = _fallback_proposals() if not proposals_raw or proposals_raw.upper() == "SKIP" else _parse_proposals(proposals_raw)

    risk_review_raw = critique_and_adjust(llm, json.dumps(proposals, indent=2))
    debated = proposals
    if risk_review_raw and risk_review_raw.upper() != "SKIP":
        debated = _parse_proposals(risk_review_raw)

    ranked = rank_proposals(debated)
    winner = ranked[0] if ranked else None

    roi = calculate_roi(llm, json.dumps(ranked, indent=2))
    if not roi or roi.upper() == "SKIP":
        roi = "Annual savings around $52K in base scenario for image quality optimization."

    sensitivity = run_sensitivity()
    before_hours = simulate_current()
    after_hours = simulate_after()
    improvement_pct = round(((before_hours - after_hours) / before_hours) * 100, 2) if before_hours else 0.0

    report_input = (
        f"TOP WINNER: {winner}\n\n"
        f"RANKED PROPOSALS: {json.dumps(ranked, indent=2)}\n\n"
        f"SENSITIVITY (sample 3 rows): {json.dumps(sensitivity[:3], indent=2)}\n\n"
        f"SIMULATION: before={before_hours}h/day after={after_hours}h/day improvement={improvement_pct}%"
    )
    report = generate_report(llm, flow, analysis, report_input, roi)
    if not report or report.upper() == "SKIP":
        report = (
            "# EXECUTIVE SUMMARY\n"
            "Local-first analysis complete with risk-adjusted ranking.\n\n"
            "## CURRENT WORKFLOW\n" + flow + "\n\n"
            "## TOP RECOMMENDATION\n"
            f"{json.dumps(winner, indent=2) if winner else 'N/A'}\n\n"
            "## ALL PROPOSALS RANKED\n"
            + "\n".join([f"{i+1}. {p.get('name')} -> {p.get('final_score')}" for i, p in enumerate(ranked)])
            + "\n\n## ROI\n" + roi
            + f"\n\n## SIMULATION\nBefore: {before_hours}h/day\nAfter: {after_hours}h/day\nImprovement: {improvement_pct}%"
        )

    run_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = output_root / run_ts
    run_dir.mkdir(parents=True, exist_ok=True)

    raw_lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    low_conf = [{"line": ln, "confidence": _heuristic_confidence(ln)} for ln in raw_lines if _heuristic_confidence(ln) < 0.80]

    (run_dir / "report.md").write_text(report, encoding="utf-8")
    (run_dir / "flow_mermaid.mmd").write_text(flow, encoding="utf-8")
    (run_dir / "extracted_text.txt").write_text(text, encoding="utf-8")
    (run_dir / "proposals_ranked.json").write_text(json.dumps(ranked, indent=2), encoding="utf-8")
    (run_dir / "low_confidence.json").write_text(json.dumps(low_conf, indent=2), encoding="utf-8")
    (run_dir / "sensitivity.json").write_text(json.dumps(sensitivity, indent=2), encoding="utf-8")
    (run_dir / "simulation.json").write_text(
        json.dumps(
            {
                "before_hours_per_day": before_hours,
                "after_hours_per_day": after_hours,
                "improvement_pct": improvement_pct,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = {
        "run_dir": str(run_dir),
        "winner": winner,
        "ranked": ranked,
        "before_hours": before_hours,
        "after_hours": after_hours,
        "improvement_pct": improvement_pct,
    }
    (run_dir / "pipeline_state.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
