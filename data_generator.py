"""Synthetic failed payment data generator for RevRescue.ai."""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker


DATA_DIR = Path(__file__).resolve().parent / "data"
OUTPUT_FILE = DATA_DIR / "failed_transactions.csv"

MERCHANTS = ["Myntra", "Swiggy", "Zomato", "Nykaa", "BookMyShow", "Ajio"]
PAYMENT_METHODS = ["UPI", "Card", "NetBanking", "Wallet"]

ERROR_CODES = [
    "INSUFFICIENT_FUNDS",
    "NETWORK_TIMEOUT",
    "BANK_DOWNTIME",
    "ABANDONED_CHECKOUT",
    "CARD_EXPIRED",
    "USER_CANCELLED",
    "FRAUD_SUSPECTED",
    "INVALID_CARD",
]

ERROR_WEIGHTS = [25, 20, 15, 20, 8, 7, 3, 2]


def _indian_phone() -> str:
    """Return a realistic Indian mobile number in +91XXXXXXXXXX format."""
    first_digit = random.choice(["6", "7", "8", "9"])
    rest = "".join(str(random.randint(0, 9)) for _ in range(9))
    return f"+91{first_digit}{rest}"


def generate_failed_transactions(batch_size: int = 75, save: bool = True) -> pd.DataFrame:
    """Generate a synthetic batch of failed payment transactions."""
    if not 1 <= batch_size <= 500:
        raise ValueError("batch_size must be between 1 and 500")

    fake = Faker("en_IN")
    Faker.seed(random.randint(1, 1_000_000))

    rows = []
    now = datetime.now()

    for index in range(batch_size):
        merchant = random.choice(MERCHANTS)
        amount = round(random.uniform(299, 7999), 2)
        failed_at = now - timedelta(minutes=random.randint(10, 60 * 48))

        rows.append(
            {
                "txn_id": f"TXN-{now.strftime('%Y%m%d')}-{index + 1:04d}",
                "customer_name": fake.name(),
                "customer_phone": _indian_phone(),
                "customer_email": fake.email(),
                "merchant": merchant,
                "amount": amount,
                "payment_method": random.choice(PAYMENT_METHODS),
                "error_code": random.choices(ERROR_CODES, weights=ERROR_WEIGHTS, k=1)[0],
                "failed_at": failed_at.strftime("%Y-%m-%d %H:%M:%S"),
                "retry_count": 0,
                "last_contact_at": "",
                "recovery_status": "PENDING",
                "recovered_amount": 0.0,
            }
        )

    df = pd.DataFrame(rows)

    if save:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUTPUT_FILE, index=False)

    return df


if __name__ == "__main__":
    generated = generate_failed_transactions()
    print(f"Generated {len(generated)} failed transactions at {OUTPUT_FILE}")
