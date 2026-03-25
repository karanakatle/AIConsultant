from __future__ import annotations

from typing import Callable


def build_flow(llm: Callable[[str], str], chunks: list[str]) -> str:
    prompt = f"""
You are Flow Builder Agent.

Task:
1) Build a concise ordered workflow from extracted text.
2) Output one Mermaid `flowchart TD` diagram.
3) If uncertain about any step names, add a `LOW_CONFIDENCE_NOTES` section.
4) Keep node labels short and business-readable.

INPUT CHUNKS:
{chunks}
""".strip()
    return llm(prompt)
