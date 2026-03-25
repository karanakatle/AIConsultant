from __future__ import annotations

from typing import Callable


def analyze_flow(llm: Callable[[str], str], flow_text: str) -> str:
    prompt = f"""
You are Understanding Agent.

Analyze the workflow and produce:
1. Current system overview
2. Key steps identified
3. Bottlenecks
4. Duplicate efforts
5. Manual interventions
6. Risk points

Rules:
- Use only evidence from input.
- If unknown, state assumption explicitly.

INPUT:
{flow_text}
""".strip()
    return llm(prompt)
