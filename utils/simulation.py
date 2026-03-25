from __future__ import annotations

from typing import List, Dict


def _simulate(steps: List[Dict]) -> float:
    total_sec = 0.0
    for s in steps:
        total_sec += s["volume"] * s["rate"] * s["time"]
    return round(total_sec / 3600, 2)


def simulate_current() -> float:
    steps = [
        {"name": "image_repair", "volume": 10000, "rate": 0.20, "time": 15},
        {"name": "fraud_review", "volume": 10000, "rate": 0.10, "time": 10},
        {"name": "reconciliation", "volume": 10000, "rate": 0.15, "time": 20},
    ]
    return _simulate(steps)


def simulate_after() -> float:
    steps = [
        {"name": "image_repair", "volume": 10000, "rate": 0.20, "time": 5},
        {"name": "fraud_review", "volume": 10000, "rate": 0.10, "time": 8},
        {"name": "reconciliation", "volume": 10000, "rate": 0.15, "time": 5},
    ]
    return _simulate(steps)
