from __future__ import annotations

from typing import Callable


def calculate_roi(llm: Callable[[str], str], proposals: str) -> str:
    prompt = f"""
You are ROI Agent.

Provide one dry-run ROI example with:
- assumptions
- formulas
- step-by-step arithmetic
- annualized value
- confidence caveats

INPUT:
{proposals}
""".strip()
    return llm(prompt)
