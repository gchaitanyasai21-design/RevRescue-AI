"""Customer intelligence profiles for deep-dive transaction inspection."""

from __future__ import annotations

import hashlib
import random
from typing import Any


def _stable_seed(txn_id: str) -> int:
    """Create a deterministic seed so the same txn always shows the same profile."""
    digest = hashlib.md5(txn_id.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _choice(rng: random.Random, options: list[Any]) -> Any:
    return options[rng.randrange(0, len(options))]


def build_customer_intelligence(txn: dict[str, Any]) -> dict[str, Any]:
    """
    Build a realistic customer intelligence card.

    Deterministic per txn_id so demo clicks feel stable and product-like.
    """
    txn_id = str(txn.get("txn_id", "TXN0"))
    rng = random.Random(_stable_seed(txn_id))

    amount = float(txn.get("amount", 0.0) or 0.0)
    error_code = str(txn.get("error_code", ""))
    method = str(txn.get("payment_method", "UPI"))

    # Risk score biased by failure type
    base_risk = {
        "FRAUD_SUSPECTED": rng.randint(82, 97),
        "USER_CANCELLED": rng.randint(25, 45),
        "INVALID_CARD": rng.randint(40, 60),
        "INSUFFICIENT_FUNDS": rng.randint(35, 55),
        "ABANDONED_CHECKOUT": rng.randint(30, 50),
        "CARD_EXPIRED": rng.randint(28, 48),
        "NETWORK_TIMEOUT": rng.randint(15, 35),
        "BANK_DOWNTIME": rng.randint(10, 30),
    }.get(error_code, rng.randint(30, 60))

    # Value tier
    if amount >= 5000:
        value_tier = "High"
        ltv = rng.randint(18000, 62000)
    elif amount >= 1500:
        value_tier = "Medium"
        ltv = rng.randint(6000, 18000)
    else:
        value_tier = "Growing"
        ltv = rng.randint(1500, 6000)

    prior_success = rng.randint(0, 6)
    prior_fail = rng.randint(0, 3)
    recovery_propensity = max(8, min(96, 100 - base_risk + rng.randint(-8, 12)))

    preferred_window = _choice(
        rng,
        ["8–10 AM", "12–2 PM", "5–7 PM", "7–9 PM", "9–11 PM"],
    )
    channel = _choice(rng, ["WhatsApp", "SMS", "App Push", "Email + WhatsApp"])
    sentiment = _choice(rng, ["Cooperative", "Neutral", "Price-sensitive", "Time-sensitive", "Anxious"])
    device = _choice(rng, ["Android / Chrome", "iOS / Safari", "Android / WebView", "Desktop / Chrome"])
    city = _choice(
        rng,
        ["Bengaluru", "Hyderabad", "Mumbai", "Pune", "Delhi NCR", "Chennai", "Jaipur", "Ahmedabad"],
    )

    if error_code == "INSUFFICIENT_FUNDS":
        recommendation = "Wait for salary window + offer EMI split. Avoid hard retry today."
        best_action = "Hinglish empathetic nudge"
    elif error_code == "ABANDONED_CHECKOUT":
        recommendation = "Strike within 30–60 mins with small incentive and one clear CTA."
        best_action = "COMEBACK5 discount nudge"
    elif error_code == "CARD_EXPIRED":
        recommendation = "Lead with UPI alternative; card update as secondary path."
        best_action = "UPI switch + card update"
    elif error_code in {"NETWORK_TIMEOUT", "BANK_DOWNTIME"}:
        recommendation = "Do not message yet. Silent infrastructure retry is optimal."
        best_action = "Auto-retry / alternate route"
    elif error_code == "FRAUD_SUSPECTED":
        recommendation = "Freeze automation. Send to risk ops with full device fingerprint."
        best_action = "Human escalation only"
    elif error_code == "USER_CANCELLED":
        recommendation = "No outreach. Preserve trust and suppress retries."
        best_action = "No action"
    else:
        recommendation = "Mark unrecoverable and exclude from outbound sequences."
        best_action = "No action"

    trust_signals = [
        f"Preferred rail: {method}",
        f"Device: {device}",
        f"City cluster: {city}",
        f"Past recoveries: {prior_success} success / {prior_fail} fail",
    ]

    return {
        "customer_name": str(txn.get("customer_name", "Customer")),
        "txn_id": txn_id,
        "merchant": str(txn.get("merchant", "Merchant")),
        "amount": amount,
        "error_code": error_code,
        "risk_score": base_risk,
        "recovery_propensity": recovery_propensity,
        "value_tier": value_tier,
        "estimated_ltv": ltv,
        "preferred_window": preferred_window,
        "best_channel": channel,
        "sentiment": sentiment,
        "best_action": best_action,
        "recommendation": recommendation,
        "trust_signals": trust_signals,
        "prior_success": prior_success,
        "prior_fail": prior_fail,
    }