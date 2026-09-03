"""Razorpay test payment link creation with demo-safe mock fallback."""

from __future__ import annotations

import os
from typing import Any

import razorpay
from dotenv import load_dotenv


load_dotenv()


def create_payment_link(txn: dict[str, Any]) -> str:
    """Create a Razorpay test payment link or return a mock link if unavailable."""
    txn_id = str(txn.get("txn_id", "unknown"))
    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")

    if not key_id or not key_secret:
        return f"https://rzp.io/i/mock-{txn_id}"

    try:
        client = razorpay.Client(auth=(key_id, key_secret))
        amount_paise = int(round(float(txn.get("amount", 0.0) or 0.0) * 100))
        payment_link = client.payment_link.create(
            {
                "amount": amount_paise,
                "currency": "INR",
                "accept_partial": False,
                "description": f"Recovery payment for {txn.get('merchant', 'merchant')} transaction {txn_id}",
                "customer": {
                    "name": txn.get("customer_name", ""),
                    "contact": txn.get("customer_phone", ""),
                    "email": txn.get("customer_email", ""),
                },
                "notify": {"sms": False, "email": False},
                "reminder_enable": False,
                "notes": {"txn_id": txn_id, "source": "RevRescue.ai"},
            }
        )
        return payment_link.get("short_url") or payment_link.get("id") or f"https://rzp.io/i/mock-{txn_id}"
    except Exception:
        return f"https://rzp.io/i/mock-{txn_id}"
