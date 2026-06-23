"""Feature extraction for interpretable 60-second, per-source-IP windows."""
from __future__ import annotations

from datetime import datetime
from urllib.parse import unquote_plus

SQLI_MARKERS = ("'", " union ", " or ", "--", "#", "select ")


def _as_time(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _has_sqli(path: str) -> bool:
    lower = unquote_plus(path).lower()
    return any(marker in lower for marker in SQLI_MARKERS)


def add_features(rows: list[dict], window_seconds: int = 60) -> list[dict]:
    """Compute features from activity by the same IP within the previous window."""
    enriched = []
    for index, row in enumerate(rows):
        now = _as_time(row["timestamp"])
        related = [candidate for candidate in rows[: index + 1] if candidate["source_ip"] == row["source_ip"] and 0 <= (now - _as_time(candidate["timestamp"])).total_seconds() <= window_seconds]
        copy = dict(row)
        # Manual DVWA brute-force practice is recorded in Apache as web
        # requests, not a separate auth.log.  Treat visits to the lab's
        # Brute Force module as failed attempts; the guide explicitly asks
        # learners to submit deliberately incorrect credentials.
        copy["failed_count"] = sum(
            item["event_type"] == "failed_login"
            or "/vulnerabilities/brute/" in item["request_path"]
            for item in related
        )
        copy["request_count"] = len(related)
        copy["unique_paths"] = len({item["request_path"] for item in related})
        copy["contains_sqli_pattern"] = int(any(_has_sqli(item["request_path"]) for item in related))
        copy["time_window"] = window_seconds
        enriched.append(copy)
    return enriched
