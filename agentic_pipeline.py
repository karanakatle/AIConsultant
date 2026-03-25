#!/usr/bin/env python3
"""Local-first end-to-end agentic workflow pipeline.

This script intentionally uses standard-library-first components so it can run in
restricted environments. It supports text-like sources directly and attempts PDF
text extraction only when optional dependencies are available.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Tuple

from roi_dry_run import RoiInputs, run as run_roi


LOW_CONFIDENCE_THRESHOLD = 0.80
REVIEW_SUGGESTED_THRESHOLD = 0.90


@dataclass
class ExtractedFact:
    step_id: str
    text: str
    lane: str
    confidence: float
    source: str


@dataclass
class PipelineResult:
    facts: List[ExtractedFact]
    review_items: List[ExtractedFact]
    diagnostics: Dict[str, List[str]]
    recommendations: Dict[str, List[str]]
    assumptions: List[str]


def read_source(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".csv", ".log"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return json.dumps(payload, indent=2)
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader  # type: ignore
        except Exception as exc:
            raise RuntimeError(
                "PDF detected but `pypdf` is not installed. "
                "Install with `python3 -m pip install pypdf` or convert PDF to text first."
            ) from exc

        text_parts: List[str] = []
        reader = PdfReader(str(path))
        for page in reader.pages:
            text_parts.append(page.extract_text() or "")
        return "\n".join(text_parts)

    raise ValueError(f"Unsupported input type: {path.suffix}")


def split_lines(raw_text: str) -> List[str]:
    lines = [ln.strip() for ln in raw_text.splitlines()]
    return [ln for ln in lines if ln]


def infer_lane(line: str) -> str:
    lowered = line.lower()
    if any(k in lowered for k in ["atm", "quick deposit", "qd"]):
        return "ATM/QD"
    if "lockbox" in lowered:
        return "Lockbox"
    if "icl" in lowered or "image cash letter" in lowered:
        return "ICL"
    if any(k in lowered for k in ["exception", "repair", "reject"]):
        return "Exceptions"
    return "General"


def score_confidence(line: str) -> float:
    score = 0.70
    if re.search(r"\b\d{1,3}(,\d{3})*\b", line):
        score += 0.08
    if len(line.split()) >= 5:
        score += 0.08
    if any(ch in line for ch in [":", "->", "=>", "%"]):
        score += 0.06
    if "???" in line or "illegible" in line.lower():
        score -= 0.30
    return max(0.0, min(0.99, round(score, 2)))


def extract_facts(lines: List[str], source_name: str) -> List[ExtractedFact]:
    facts: List[ExtractedFact] = []
    for idx, line in enumerate(lines, start=1):
        confidence = score_confidence(line)
        lane = infer_lane(line)
        facts.append(
            ExtractedFact(
                step_id=f"S{idx:03d}",
                text=line,
                lane=lane,
                confidence=confidence,
                source=source_name,
            )
        )
    return facts


def build_diagnostics(facts: List[ExtractedFact]) -> Dict[str, List[str]]:
    duplicates: List[str] = []
    normalized: Dict[str, int] = {}
    for f in facts:
        norm = re.sub(r"\s+", " ", f.text.lower())
        normalized[norm] = normalized.get(norm, 0) + 1
    for text, count in normalized.items():
        if count > 1:
            duplicates.append(f"Repeated step ({count}x): {text[:120]}")

    handoff_markers = [f for f in facts if any(x in f.text.lower() for x in ["handoff", "queue", "send to", "route to"])]
    manual_markers = [f for f in facts if any(x in f.text.lower() for x in ["manual", "review", "exception", "repair"])]

    findings = {
        "bottlenecks": [
            "High manual handling concentration detected." if manual_markers else "No explicit manual bottleneck markers detected."
        ],
        "duplication": duplicates or ["No exact duplicate steps detected."],
        "handoffs": [f"Potential handoff point: {f.step_id} {f.text}" for f in handoff_markers[:10]]
        or ["No explicit handoff markers found."],
    }
    return findings


def classify_recommendations(diagnostics: Dict[str, List[str]]) -> Dict[str, List[str]]:
    category_1 = [
        "Deploy an exception-summary copilot that drafts queue notes for human approval.",
        "Add daily volume variance alerts per channel (ATM/QD/Lockbox/ICL).",
    ]
    category_2 = [
        "Implement cross-queue orchestration recommendations to balance workload across teams.",
        "Add diagram-to-checklist conversion agent for standardized operations onboarding.",
    ]
    category_3 = [
        "Avoid fully autonomous pay/no-pay decisioning until governance and controls are mature.",
        "Avoid autonomous funds-release decisions without mandatory human sign-off.",
    ]

    if diagnostics.get("duplication") and diagnostics["duplication"][0] != "No exact duplicate steps detected.":
        category_1.append("Add duplicate-step detector in daily run to flag redundant work items.")

    return {
        "easy_high_roi_low_risk": category_1,
        "hard_high_roi_low_risk": category_2,
        "very_risky": category_3,
    }


def mermaid_from_facts(facts: List[ExtractedFact]) -> str:
    lines = ["flowchart TD"]
    for idx, fact in enumerate(facts, start=1):
        node = f"N{idx}"
        label = f"{fact.step_id} [{fact.lane}] {fact.text}".replace('"', "'")
        lines.append(f"    {node}[\"{label}\"]")
        if idx > 1:
            lines.append(f"    N{idx-1} --> {node}")
    return "\n".join(lines)


def write_outputs(out_dir: Path, result: PipelineResult, mermaid_text: str, roi: Dict[str, float]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    details_dir = out_dir / "03_mermaid_detailed"
    details_dir.mkdir(exist_ok=True)

    (out_dir / "02_mermaid_high_level.mmd").write_text(mermaid_text, encoding="utf-8")
    (details_dir / "process_flow.mmd").write_text(mermaid_text, encoding="utf-8")

    summary_lines = [
        "# Current State Summary",
        "",
        f"Generated at: {datetime.now(timezone.utc).isoformat()}",
        f"Total extracted steps: {len(result.facts)}",
        f"Items requiring human review: {len(result.review_items)}",
        "",
        "## Diagnostics",
    ]
    for k, vals in result.diagnostics.items():
        summary_lines.append(f"### {k.title()}")
        for v in vals:
            summary_lines.append(f"- {v}")
        summary_lines.append("")
    (out_dir / "01_current_state_summary.md").write_text("\n".join(summary_lines), encoding="utf-8")

    assumptions_md = "# Assumptions Log\n\n" + "\n".join(f"- {a}" for a in result.assumptions)
    (out_dir / "04_assumptions_log.md").write_text(assumptions_md, encoding="utf-8")

    rec_lines = ["# Recommendations by Risk Category", ""]
    for category, recs in result.recommendations.items():
        rec_lines.append(f"## {category}")
        for r in recs:
            rec_lines.append(f"- {r}")
        rec_lines.append("")
    (out_dir / "05_recommendations_by_risk.md").write_text("\n".join(rec_lines), encoding="utf-8")

    roi_lines = [
        "# ROI Dry Run",
        "",
        "Assumptions use defaults from `RoiInputs`.",
        "",
    ]
    for k, v in roi.items():
        roi_lines.append(f"- **{k}**: {v:,.2f}")
    (out_dir / "06_roi_dry_run.md").write_text("\n".join(roi_lines), encoding="utf-8")

    review_lines = ["# Human Review Queue", ""]
    for item in result.review_items:
        review_lines.append(f"- {item.step_id} ({item.confidence:.2f}): {item.text}")
    if not result.review_items:
        review_lines.append("- No mandatory review items.")
    (out_dir / "review_queue.md").write_text("\n".join(review_lines), encoding="utf-8")

    json_payload = {
        "facts": [asdict(f) for f in result.facts],
        "review_items": [asdict(f) for f in result.review_items],
        "diagnostics": result.diagnostics,
        "recommendations": result.recommendations,
        "assumptions": result.assumptions,
        "roi": roi,
    }
    (out_dir / "run.json").write_text(json.dumps(json_payload, indent=2), encoding="utf-8")


def run_pipeline(input_path: Path, output_dir: Path) -> Path:
    raw_text = read_source(input_path)
    lines = split_lines(raw_text)
    facts = extract_facts(lines, input_path.name)
    review_items = [f for f in facts if f.confidence < LOW_CONFIDENCE_THRESHOLD]
    diagnostics = build_diagnostics(facts)
    recommendations = classify_recommendations(diagnostics)

    assumptions = [
        "Input text order approximates process sequence.",
        "Confidence scores are heuristic and should be calibrated with historical data.",
        "Recommendations are advisory; human oversight remains required.",
    ]

    result = PipelineResult(
        facts=facts,
        review_items=review_items,
        diagnostics=diagnostics,
        recommendations=recommendations,
        assumptions=assumptions,
    )

    mermaid_text = mermaid_from_facts(facts[:60])  # cap for readability
    roi = run_roi(RoiInputs())

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = output_dir / timestamp
    write_outputs(run_dir, result, mermaid_text, roi)
    return run_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local-first agentic workflow pipeline")
    parser.add_argument("--input", required=True, help="Path to input .txt/.md/.json/.pdf")
    parser.add_argument("--output", default="runs", help="Output directory root")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = run_pipeline(Path(args.input), Path(args.output))
    print(f"Pipeline complete. Outputs written to: {run_dir}")


if __name__ == "__main__":
    main()
