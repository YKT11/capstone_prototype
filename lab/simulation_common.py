"""Shared safe logging utilities for the four lab simulations."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_LOGS = ROOT / "data" / "raw_logs"
MANIFEST = RAW_LOGS / "simulation_manifest.csv"


def record_phase(source_ip: str, label: str) -> None:
    """Append source-IP ground truth used later by the dataset builder."""
    RAW_LOGS.mkdir(parents=True, exist_ok=True)
    write_header = not MANIFEST.exists()
    with MANIFEST.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source_ip", "label", "recorded_at"])
        if write_header:
            writer.writeheader()
        writer.writerow({"source_ip": source_ip, "label": label, "recorded_at": datetime.now(timezone.utc).isoformat()})


def write_auth_failure(source_ip: str, username: str = "admin") -> None:
    """Write a syslog-shaped auth event because DVWA itself has no auth.log."""
    RAW_LOGS.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%b %d %H:%M:%S")
    with (RAW_LOGS / "auth.log").open("a", encoding="utf-8") as handle:
        handle.write(f"{timestamp} cyberlab dvwa-auth: Failed password for {username} from {source_ip} port 0 ssh2\n")
