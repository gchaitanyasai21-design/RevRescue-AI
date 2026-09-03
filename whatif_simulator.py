"""What-If Strategy Simulator for RevRescue.ai."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class WhatIfInputs:
    max_retries: int = 3
    discount_pct: int = 5
    contact_hour: int = 19  # 0-23
    emi_push_strength: int = 1  # 0 quiet, 1 normal, 2 aggressive
    alt_route_priority: int = 1  # 0 off, 1 on
    cooling_off_hours: float = 2.0


def _clip(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _base_success_rate(error_code: str) -> float:
    return {
        "INSUFFICIENT_FUNDS": 0.45,
        "NETWORK_TIMEOUT": 0.75,
        "BANK_DOWNTIME": 0.68,
        "ABANDONED_CHECKOUT": 0.35,
        "CARD_EXPIRED": 0.40,
        "USER_CANCELLED": 0.0,
        "FRAUD_SUSPECTED": 0.0,
        "INVALID_CARD": 0.0,
    }.get(error_code, 0.25)


def _is_contact_strategy(error_code: str) -> bool:
    return error_code in {"INSUFFICIENT_FUNDS", "ABANDONED_CHECKOUT", "CARD_EXPIRED"}


def _is_infra_strategy(error_code: str) -> bool:
    return error_code in {"NETWORK_TIMEOUT", "BANK_DOWNTIME"}


def estimate_success_rate(error_code: str, inputs: WhatIfInputs) -> float:
    """Estimate modified success probability under what-if levers."""
    base = _base_success_rate(error_code)
    if base <= 0:
        return 0.0

    rate = base

    # Retry lever
    retry_bonus = (inputs.max_retries - 3) * (0.035 if _is_infra_strategy(error_code) else 0.015)
    rate += retry_bonus

    # Discount lever
    discount_delta = inputs.discount_pct - 5
    if error_code == "ABANDONED_CHECKOUT":
        rate += discount_delta * 0.012
    elif _is_contact_strategy(error_code):
        rate += discount_delta * 0.004

    # Contact timing lever (peak around 19:00)
    timing_gap = abs(inputs.contact_hour - 19)
    timing_bonus = _clip(0.06 - 0.01 * timing_gap, -0.04, 0.06)
    if _is_contact_strategy(error_code):
        rate += timing_bonus

    # EMI push strength
    if error_code == "INSUFFICIENT_FUNDS":
        rate += (inputs.emi_push_strength - 1) * 0.04

    # Alternate route priority
    if error_code == "BANK_DOWNTIME":
        rate += 0.05 if inputs.alt_route_priority else -0.08
    if error_code == "NETWORK_TIMEOUT":
        rate += 0.02 if inputs.alt_route_priority else -0.03

    # Cooling-off effects
    if _is_contact_strategy(error_code):
        if inputs.cooling_off_hours < 1:
            rate -= 0.05
        elif inputs.cooling_off_hours > 4:
            rate -= 0.02

    return _clip(rate, 0.0, 0.95)


def simulate_whatif(df: pd.DataFrame, inputs: WhatIfInputs) -> dict[str, Any]:
    """
    Run a deterministic expected-value simulation on the current batch.
    Returns KPIs + per-error breakdown for charts.
    """
    if df.empty:
        return {
            "expected_recovered": 0.0,
            "expected_rate": 0.0,
            "baseline_recovered": 0.0,
            "baseline_rate": 0.0,
            "delta_recovered": 0.0,
            "delta_rate_pp": 0.0,
            "recoverable_txns": 0,
            "blocked_txns": 0,
            "by_error": pd.DataFrame(),
            "total_amount": 0.0,
        }

    rows = []
    expected_recovered = 0.0
    baseline_recovered = 0.0
    recoverable_txns = 0
    blocked_txns = 0

    for _, row in df.iterrows():
        error_code = str(row.get("error_code", ""))
        amount = float(row.get("amount", 0.0) or 0.0)

        base_rate = _base_success_rate(error_code)
        new_rate = estimate_success_rate(error_code, inputs)

        if base_rate <= 0:
            blocked_txns += 1
            effective_rate = 0.0
        else:
            recoverable_txns += 1
            effective_rate = new_rate

        exp_amt = amount * effective_rate
        base_amt = amount * base_rate

        expected_recovered += exp_amt
        baseline_recovered += base_amt

        rows.append(
            {
                "error_code": error_code,
                "amount": amount,
                "baseline_rate": base_rate,
                "whatif_rate": effective_rate,
                "baseline_expected": base_amt,
                "whatif_expected": exp_amt,
            }
        )

    total_amount = float(df["amount"].sum())
    expected_rate = (expected_recovered / total_amount) if total_amount else 0.0
    baseline_rate = (baseline_recovered / total_amount) if total_amount else 0.0

    by_error = (
        pd.DataFrame(rows)
        .groupby("error_code", as_index=False)
        .agg(
            txn_count=("amount", "count"),
            amount=("amount", "sum"),
            baseline_expected=("baseline_expected", "sum"),
            whatif_expected=("whatif_expected", "sum"),
            baseline_rate=("baseline_rate", "mean"),
            whatif_rate=("whatif_rate", "mean"),
        )
    )
    by_error["delta_expected"] = by_error["whatif_expected"] - by_error["baseline_expected"]

    return {
        "expected_recovered": expected_recovered,
        "expected_rate": expected_rate,
        "baseline_recovered": baseline_recovered,
        "baseline_rate": baseline_rate,
        "delta_recovered": expected_recovered - baseline_recovered,
        "delta_rate_pp": (expected_rate - baseline_rate) * 100,
        "recoverable_txns": recoverable_txns,
        "blocked_txns": blocked_txns,
        "by_error": by_error,
        "total_amount": total_amount,
    }