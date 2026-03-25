#!/usr/bin/env python3
"""Simple ROI dry-run calculator for agentic workflow opportunities."""

from dataclasses import dataclass


@dataclass
class RoiInputs:
    daily_volume: int = 100_000
    manual_exception_rate: float = 0.04
    current_minutes_per_item: float = 3.5
    reduction_pct: float = 0.25
    loaded_labor_per_hour: float = 42.0
    workdays_per_year: int = 250
    annual_run_cost: float = 120_000.0


def run(inputs: RoiInputs) -> dict:
    manual_items_per_day = inputs.daily_volume * inputs.manual_exception_rate
    minutes_saved_per_item = inputs.current_minutes_per_item * inputs.reduction_pct
    minutes_saved_per_day = manual_items_per_day * minutes_saved_per_item
    hours_saved_per_day = minutes_saved_per_day / 60
    daily_value = hours_saved_per_day * inputs.loaded_labor_per_hour
    annual_value = daily_value * inputs.workdays_per_year
    net_benefit = annual_value - inputs.annual_run_cost
    roi_multiple = net_benefit / inputs.annual_run_cost

    return {
        "manual_items_per_day": manual_items_per_day,
        "minutes_saved_per_item": minutes_saved_per_item,
        "minutes_saved_per_day": minutes_saved_per_day,
        "hours_saved_per_day": hours_saved_per_day,
        "daily_value": daily_value,
        "annual_value": annual_value,
        "net_benefit": net_benefit,
        "roi_multiple": roi_multiple,
    }


if __name__ == "__main__":
    result = run(RoiInputs())
    print("ROI Dry Run (example assumptions)\n")
    for key, value in result.items():
        if isinstance(value, float):
            print(f"{key:24} {value:,.2f}")
        else:
            print(f"{key:24} {value:,}")
