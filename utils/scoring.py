from __future__ import annotations

from typing import List, Dict


def compute_final_score(p: Dict) -> float:
    return round(
        (p.get("roi_score", 0) * 0.4)
        + (p.get("ease_score", 0) * 0.2)
        + (p.get("confidence_score", 0) * 0.2)
        - (p.get("risk_score", 0) * 0.2),
        2,
    )


def rank_proposals(proposals: List[Dict]) -> List[Dict]:
    for p in proposals:
        p["final_score"] = compute_final_score(p)
    return sorted(proposals, key=lambda x: x["final_score"], reverse=True)
