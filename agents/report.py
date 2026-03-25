from __future__ import annotations

from typing import Callable


def generate_report(llm: Callable[[str], str], flow: str, analysis: str, proposals: str, roi: str) -> str:
    prompt = f"""
You are Report Generator Agent.

Create a presentation-ready business document with sections:
1. Executive Summary
2. Current Workflow (include Mermaid)
3. Key Issues
4. Proposed Agentic AI Solutions (3 categories)
5. ROI Dry Run
6. Assumptions Register
7. Risks & Mitigations
8. Next 30-60-90 day plan

FLOW:
{flow}

ANALYSIS:
{analysis}

PROPOSALS:
{proposals}

ROI:
{roi}
""".strip()
    return llm(prompt)
