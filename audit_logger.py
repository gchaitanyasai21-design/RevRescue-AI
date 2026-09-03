"""File-based audit trail for RevRescue.ai."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent / "data"
LOG_FILE = DATA_DIR / "audit_trail.log"
VALID_STATUSES = {"INFO", "SUCCESS", "WARNING", "ERROR"}


def log_action(txn_id: str, action: str, details: str, status: str = "INFO") -> None:
    """Append one readable audit event to the log file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    safe_status = status if status in VALID_STATUSES else "INFO"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{safe_status}] {txn_id}: {action} — {details}\n"
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(line)


def get_audit_trail(limit: int = 200) -> list[str]:
    """Return the most recent audit lines first."""
    if not LOG_FILE.exists():
        return []
    with LOG_FILE.open("r", encoding="utf-8") as file:
        lines = [line.rstrip("\n") for line in file.readlines()]
    return list(reversed(lines[-limit:]))


def clear_audit_trail() -> None:
    """Reset the audit log for a fresh demo run."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.write_text("", encoding="utf-8")
