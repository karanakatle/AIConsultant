from __future__ import annotations

from typing import Callable


def propose_agents(llm: Callable[[str], str], analysis: str) -> str:
    prompt = f"""
You are Optimization Agent.

Based on the analysis, propose agentic AI improvements in exactly 3 categories:
1) Easy to implement + high ROI + minimal risk
2) Hard to implement + high ROI + minimal risk
3) Very risky implementation with major downside if wrong

For each recommendation include:
- Problem
- Proposed agent
- Why this is agentic AI
- Expected value driver
- Failure impact
- Human override/control
- Assumptions

INPUT:
{analysis}
""".strip()
    return llm(prompt)
