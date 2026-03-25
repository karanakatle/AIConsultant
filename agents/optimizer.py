from __future__ import annotations

from typing import Callable


def propose_agents(llm: Callable[[str], str], analysis: str) -> str:
    prompt = f"""
You are Optimization Agent.

Propose agentic AI solutions and return STRICT JSON array.
Each item must include:
- name
- description
- category (Easy/Hard/Risky)
- roi_score (0-10)
- ease_score (0-10)
- risk_score (0-10)
- confidence_score (0-10)
- confidence_reason
- assumptions (array)

Scoring rubric:
- confidence 10: clear evidence + minimal assumptions
- confidence 7-9: minor assumptions
- confidence 4-6: moderate ambiguity
- confidence 1-3: high uncertainty

INPUT:
{analysis}
""".strip()
    return llm(prompt)
