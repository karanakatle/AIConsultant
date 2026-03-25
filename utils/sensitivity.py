from __future__ import annotations

import itertools
from typing import List, Dict


def compute_savings(volume: int, time_saved_sec: float, automation_rate: float, cost_per_hour: float) -> float:
    total_sec = volume * time_saved_sec * automation_rate
    hours = total_sec / 3600
    return hours * cost_per_hour


def run_sensitivity() -> List[Dict]:
    volumes = [8000, 10000, 12000]
    times = [5, 10, 15]
    automation = [0.4, 0.6, 0.8]
    cost = 25

    results = []
    for v, t, a in itertools.product(volumes, times, automation):
        daily = compute_savings(v, t, a, cost)
        results.append(
            {
                "volume": v,
                "time_saved_sec": t,
                "automation_rate": a,
                "daily_savings": round(daily, 2),
                "monthly_savings": round(daily * 30, 2),
                "annual_savings": round(daily * 250, 2),
            }
        )
    return results
