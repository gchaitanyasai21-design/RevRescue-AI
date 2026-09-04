"""Multi-merchant intelligence and filtering for RevRescue.ai."""

from __future__ import annotations

from typing import Any

import pandas as pd


# Merchant metadata — makes each feel like a real business
MERCHANT_PROFILES: dict[str, dict[str, Any]] = {
    "Myntra": {
        "category": "Fashion & Lifestyle",
        "avg_ticket_size": "₹1,500 – ₹3,000",
        "peak_hours": "7–10 PM",
        "primary_channel": "App Push + WhatsApp",
        "tone": "Trendy, discount-driven",
        "top_failure_type": "Abandoned Checkout",
        "logo_emoji": "👗",
        "brand_color": "#ff3f6c",
    },
    "Swiggy": {
        "category": "Food Delivery",
        "avg_ticket_size": "₹300 – ₹800",
        "peak_hours": "12–2 PM, 7–10 PM",
        "primary_channel": "App Push",
        "tone": "Urgent, hunger-driven",
        "top_failure_type": "Insufficient Funds",
        "logo_emoji": "🍔",
        "brand_color": "#fc8019",
    },
    "Zomato": {
        "category": "Food Delivery",
        "avg_ticket_size": "₹350 – ₹900",
        "peak_hours": "1–3 PM, 8–10 PM",
        "primary_channel": "App Push + SMS",
        "tone": "Playful, quick",
        "top_failure_type": "Insufficient Funds",
        "logo_emoji": "🍕",
        "brand_color": "#e23744",
    },
    "Nykaa": {
        "category": "Beauty & Cosmetics",
        "avg_ticket_size": "₹800 – ₹2,500",
        "peak_hours": "6–9 PM",
        "primary_channel": "WhatsApp + Email",
        "tone": "Elegant, empathetic",
        "top_failure_type": "Card Expired",
        "logo_emoji": "💄",
        "brand_color": "#fc2779",
    },
    "BookMyShow": {
        "category": "Entertainment & Ticketing",
        "avg_ticket_size": "₹250 – ₹1,200",
        "peak_hours": "5–9 PM (Fri-Sun peak)",
        "primary_channel": "SMS + WhatsApp",
        "tone": "Time-sensitive, urgent",
        "top_failure_type": "Network Timeout",
        "logo_emoji": "🎬",
        "brand_color": "#c4242b",
    },
    "Ajio": {
        "category": "Fashion & Apparel",
        "avg_ticket_size": "₹1,200 – ₹2,800",
        "peak_hours": "8–11 PM",
        "primary_channel": "App Push + WhatsApp",
        "tone": "Aspirational, discount-driven",
        "top_failure_type": "Abandoned Checkout",
        "logo_emoji": "🛍️",
        "brand_color": "#2e2e2e",
    },
}


def get_all_merchants(df: pd.DataFrame) -> list[str]:
    """Return sorted list of unique merchants present in the batch."""
    if df.empty or "merchant" not in df.columns:
        return []
    return sorted(df["merchant"].dropna().unique().tolist())


def filter_by_merchant(df: pd.DataFrame, merchant: str) -> pd.DataFrame:
    """Filter transactions by merchant. 'All Merchants' returns full df."""
    if merchant == "All Merchants" or df.empty:
        return df
    return df[df["merchant"] == merchant].copy()


def compute_merchant_stats(df: pd.DataFrame, merchant: str) -> dict[str, Any]:
    """Compute per-merchant KPIs."""
    filtered = filter_by_merchant(df, merchant)
    if filtered.empty:
        return {
            "txn_count": 0,
            "total_failed": 0.0,
            "total_recovered": 0.0,
            "recovery_rate": 0.0,
            "avg_ticket": 0.0,
            "top_failure": "N/A",
            "unrecoverable": 0,
        }

    total_failed = float(filtered["amount"].sum())
    total_recovered = (
        float(filtered["recovered_amount"].sum())
        if "recovered_amount" in filtered.columns
        else 0.0
    )
    recovery_rate = (total_recovered / total_failed * 100) if total_failed else 0.0
    top_failure = (
        filtered["error_code"].value_counts().index[0]
        if len(filtered) > 0
        else "N/A"
    )
    unrecoverable = (
        int((filtered["recovery_status"] == "UNRECOVERABLE").sum())
        if "recovery_status" in filtered.columns
        else 0
    )

    return {
        "txn_count": len(filtered),
        "total_failed": total_failed,
        "total_recovered": total_recovered,
        "recovery_rate": recovery_rate,
        "avg_ticket": float(filtered["amount"].mean()) if len(filtered) else 0.0,
        "top_failure": top_failure,
        "unrecoverable": unrecoverable,
    }


def get_merchant_profile(merchant: str) -> dict[str, Any]:
    """Return static merchant profile metadata."""
    return MERCHANT_PROFILES.get(
        merchant,
        {
            "category": "General Merchant",
            "avg_ticket_size": "Varies",
            "peak_hours": "Varies",
            "primary_channel": "WhatsApp + SMS",
            "tone": "Balanced",
            "top_failure_type": "Mixed",
            "logo_emoji": "🏪",
            "brand_color": "#ffb84d",
        },
    )


def rank_merchants(df: pd.DataFrame) -> pd.DataFrame:
    """Return a ranking table of merchants by recovery performance."""
    if df.empty:
        return pd.DataFrame()

    merchants = get_all_merchants(df)
    rows = []
    for m in merchants:
        stats = compute_merchant_stats(df, m)
        rows.append(
            {
                "Merchant": m,
                "Txns": stats["txn_count"],
                "Failed Amount": stats["total_failed"],
                "Recovered": stats["total_recovered"],
                "Recovery Rate %": round(stats["recovery_rate"], 1),
                "Top Failure": stats["top_failure"],
            }
        )
    return pd.DataFrame(rows).sort_values("Recovery Rate %", ascending=False)