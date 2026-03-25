from __future__ import annotations

from typing import Callable


def critique_and_adjust(llm: Callable[[str], str], proposals_json: str) -> str:
    prompt = f"""
You are a Risk and Compliance Officer.

Given proposal JSON:
1) Increase risk_score if optimistic.
2) Reduce confidence_score when assumptions are weak.
3) Add risk_notes and mitigation fields.
4) Return STRICT JSON only.

INPUT:
{proposals_json}
""".strip()
    return llm(prompt)
