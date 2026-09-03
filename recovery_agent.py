"""Rule-based recovery decision engine for RevRescue.ai."""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any


MAX_RETRIES = 3
COOLING_OFF_HOURS = 2

RECOVERY_STRATEGIES: dict[str, dict[str, Any]] = {
    "INSUFFICIENT_FUNDS": {
        "action": "SEND_HINGLISH_NUDGE",
        "delay_hours": 12,
        "message_type": "empathetic_alternative",
        "success_rate": 0.45,
        "description": "Send an empathetic EMI/alternate timing nudge and payment link.",
    },
    "NETWORK_TIMEOUT": {
        "action": "AUTO_RETRY",
        "delay_hours": 0,
        "message_type": None,
        "success_rate": 0.75,
        "description": "Retry silently because the failure was likely transient network instability.",
    },
    "BANK_DOWNTIME": {
        "action": "AUTO_RETRY_ALT_ROUTE",
        "delay_hours": 1,
        "message_type": None,
        "success_rate": 0.68,
        "description": "Retry through an alternate route after bank downtime is likely resolved.",
    },
    "ABANDONED_CHECKOUT": {
        "action": "SEND_HINGLISH_NUDGE",
        "delay_hours": 1,
        "message_type": "discount_urgency",
        "success_rate": 0.35,
        "description": "Send a gentle comeback message with COMEBACK5 urgency.",
    },
    "CARD_EXPIRED": {
        "action": "SEND_HINGLISH_NUDGE",
        "delay_hours": 0,
        "message_type": "card_update",
        "success_rate": 0.40,
        "description": "Ask customer to update card or switch to UPI.",
    },
    "USER_CANCELLED": {
        "action": "NO_ACTION",
        "delay_hours": 0,
        "message_type": None,
        "success_rate": 0.0,
        "description": "Respect user choice; no automated recovery attempt.",
    },
    "FRAUD_SUSPECTED": {
        "action": "ESCALATE_TO_HUMAN",
        "delay_hours": 0,
        "message_type": None,
        "success_rate": 0.0,
        "description": "Escalate to human risk review; never auto-recover suspected fraud.",
    },
    "INVALID_CARD": {
        "action": "NO_ACTION",
        "delay_hours": 0,
        "message_type": None,
        "success_rate": 0.0,
        "description": "Invalid payment instrument; customer must initiate a fresh valid payment.",
    },
}

NON_RECOVERABLE_ACTIONS = {"NO_ACTION", "ESCALATE_TO_HUMAN"}


def _parse_datetime(value: Any) -> datetime | None:
    if value is None or str(value).strip() in {"", "nan", "NaT"}:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        try:
            return datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None


def diagnose_and_strategize(txn: dict[str, Any]) -> dict[str, Any]:
    """Diagnose a failed transaction and return a strategy with compliance checks."""
    error_code = str(txn.get("error_code", "")).upper()
    base_strategy = RECOVERY_STRATEGIES.get(
        error_code,
        {
            "action": "NO_ACTION",
            "delay_hours": 0,
            "message_type": None,
            "success_rate": 0.0,
            "description": f"Unknown error code {error_code}; no automated recovery.",
        },
    )

    strategy = {
        **base_strategy,
        "error_code": error_code,
        "compliance_blocked": False,
        "block_reason": "",
        "is_recoverable": base_strategy["action"] not in NON_RECOVERABLE_ACTIONS,
    }

    retry_count = int(txn.get("retry_count") or 0)
    if retry_count >= MAX_RETRIES and strategy["is_recoverable"]:
        strategy.update(
            {
                "action": "COMPLIANCE_BLOCK",
                "success_rate": 0.0,
                "compliance_blocked": True,
                "is_recoverable": False,
                "block_reason": f"Max retry limit reached ({retry_count}/{MAX_RETRIES}).",
                "description": "Blocked by stopping rules to prevent excessive recovery attempts.",
            }
        )
        return strategy

    last_contact_at = _parse_datetime(txn.get("last_contact_at"))
    if last_contact_at and strategy["action"] == "SEND_HINGLISH_NUDGE":
        next_allowed_at = last_contact_at + timedelta(hours=COOLING_OFF_HOURS)
        if datetime.now() < next_allowed_at:
            strategy.update(
                {
                    "action": "COMPLIANCE_BLOCK",
                    "success_rate": 0.0,
                    "compliance_blocked": True,
                    "is_recoverable": False,
                    "block_reason": (
                        "Cooling-off period active until "
                        f"{next_allowed_at.strftime('%Y-%m-%d %H:%M:%S')}."
                    ),
                    "description": "Blocked by customer contact cooling-off rules.",
                }
            )

    return strategy


def simulate_recovery(txn: dict[str, Any], strategy: dict[str, Any]) -> tuple[bool, float]:
    """Simulate whether a recovery attempt succeeds based on configured probability."""
    success_rate = float(strategy.get("success_rate", 0.0) or 0.0)
    if success_rate <= 0:
        return False, 0.0

    success = random.random() < success_rate
    amount = float(txn.get("amount", 0.0) or 0.0)
    return success, round(amount, 2) if success else 0.0
