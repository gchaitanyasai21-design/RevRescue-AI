"""Simulated AI chain-of-thought reasoning for live agent display."""

from __future__ import annotations

import random
from typing import Any


REASONING_TEMPLATES: dict[str, list[str]] = {
    "INSUFFICIENT_FUNDS": [
        "🔍 Scanning wallet/bank response codes...",
        "💭 Signal: decline likely due to low balance, not customer abandonment",
        "📊 Pattern match: Indian salary-cycle recoveries peak on 1st / 7th / 15th",
        "🧠 High-empathy + EMI framing outperforms hard retry for this class",
        "⚡ Strategy locked: Hinglish nudge with EMI / retry-later option",
        "✅ Confidence: {confidence}% | Expected recoverable value: ₹{expected}",
    ],
    "NETWORK_TIMEOUT": [
        "🔍 Inspecting gateway latency + timeout fingerprint...",
        "💭 Transient infrastructure failure — customer intent still intact",
        "📊 Historical silent-retry success window: 45–90 minutes",
        "🧠 Contacting customer now would create unnecessary friction",
        "⚡ Strategy locked: Silent auto-retry on primary route",
        "✅ Confidence: {confidence}% | Expected recoverable value: ₹{expected}",
    ],
    "BANK_DOWNTIME": [
        "🔍 Acquirer response classifies as bank-side 5xx / downtime",
        "💭 Failure is route-specific, not payment-instrument specific",
        "📊 Secondary PSP route shows materially better completion odds",
        "🧠 Reroute quietly — zero customer spam, maximum recovery speed",
        "⚡ Strategy locked: Auto-retry via alternate payment route",
        "✅ Confidence: {confidence}% | Expected recoverable value: ₹{expected}",
    ],
    "ABANDONED_CHECKOUT": [
        "🔍 Funnel drop detected at payment step...",
        "💭 High purchase intent, low completion commitment",
        "📊 Soft urgency + small incentive lifts conversion in first 30–60 mins",
        "🧠 Deploy Hinglish reminder with limited-time 5% code COMEBACK5",
        "⚡ Strategy locked: Discount nudge + payment link",
        "✅ Confidence: {confidence}% | Expected recoverable value: ₹{expected}",
    ],
    "CARD_EXPIRED": [
        "🔍 Card metadata indicates expiry / stale credential",
        "💭 Customer may be unaware — not a hard rejection of purchase",
        "📊 UPI fallback converts a meaningful share of expired-card failures",
        "🧠 Offer card update OR one-tap UPI alternative",
        "⚡ Strategy locked: Hinglish card-update + UPI nudge",
        "✅ Confidence: {confidence}% | Expected recoverable value: ₹{expected}",
    ],
    "USER_CANCELLED": [
        "🔍 Explicit cancellation event captured from checkout",
        "💭 Customer intent is clear — do not override consent",
        "🧠 Any recovery attempt here would be non-compliant and brand-negative",
        "⚡ Strategy locked: NO ACTION",
        "✅ Honest exception recorded | Confidence: {confidence}%",
    ],
    "FRAUD_SUSPECTED": [
        "🚨 Risk engine flags velocity / geo / instrument anomalies",
        "💭 Automated recovery could amplify fraud exposure",
        "🧠 Route to human review queue only — never auto-charge or auto-nudge",
        "⚡ Strategy locked: ESCALATE TO HUMAN",
        "✅ Compliance hold engaged | Confidence: {confidence}%",
    ],
    "INVALID_CARD": [
        "🔍 Instrument failed validation (BIN / Luhn / status)",
        "💭 This is a data validity failure, not a recoverable intent gap",
        "🧠 No compliant automated recovery path available",
        "⚡ Strategy locked: NO ACTION",
        "✅ Honest exception recorded | Confidence: {confidence}%",
    ],
}


def generate_reasoning_stream(txn: dict[str, Any], strategy: dict[str, Any]) -> list[str]:
    """Return a chain-of-thought style reasoning stream for one transaction."""
    error_code = str(txn.get("error_code", "INSUFFICIENT_FUNDS"))
    lines = REASONING_TEMPLATES.get(error_code, REASONING_TEMPLATES["INSUFFICIENT_FUNDS"])

    confidence = random.randint(74, 96)
    success_rate = float(strategy.get("success_rate", 0.0) or 0.0)
    amount = float(txn.get("amount", 0.0) or 0.0)
    expected = int(amount * success_rate)

    return [line.format(confidence=confidence, expected=f"{expected:,}") for line in lines]