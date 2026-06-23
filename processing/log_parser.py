"""Regex-based parsers for Apache combined logs and local auth-style events."""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Iterable

APACHE = re.compile(r'^(?P<source_ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] "(?P<method>\S+) (?P<path>.*?) \S+" (?P<status_code>\d{3})')
AUTH = re.compile(r'^(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}).*Failed password for (?P<username>\S+) from (?P<source_ip>\S+)')


def _apache_timestamp(value: str) -> str:
    return datetime.strptime(value.split()[0], "%d/%b/%Y:%H:%M:%S").isoformat(sep=" ")


def parse_apache_lines(lines: Iterable[str]) -> list[dict]:
    """Return normalized web rows; lines outside combined format are ignored."""
    rows = []
    for line in lines:
        match = APACHE.match(line)
        if not match:
            continue
        data = match.groupdict()
        try:
            timestamp = _apache_timestamp(data["timestamp"])
        except ValueError:
            timestamp = data["timestamp"]
        rows.append({"timestamp": timestamp, "source_ip": data["source_ip"], "event_type": "web_request", "request_path": data["path"], "status_code": int(data["status_code"]), "username": ""})
    return rows


def parse_auth_lines(lines: Iterable[str], year: int | None = None) -> list[dict]:
    """Parse the auth-shaped entries created by the brute-force simulator."""
    rows = []
    for line in lines:
        match = AUTH.match(line)
        if not match:
            continue
        data = match.groupdict()
        parsed_year = year or datetime.now().year
        timestamp = datetime.strptime(f"{parsed_year} {data['timestamp']}", "%Y %b %d %H:%M:%S").isoformat(sep=" ")
        rows.append({"timestamp": timestamp, "source_ip": data["source_ip"], "event_type": "failed_login", "request_path": "/DVWA/vulnerabilities/brute/", "status_code": 401, "username": data["username"]})
    return rows


def parse_logs(access_log: Path, auth_log: Path) -> list[dict]:
    """Load both expected log sources, treating missing files as empty sources."""
    apache_lines = access_log.read_text(encoding="utf-8", errors="replace").splitlines() if access_log.exists() else []
    auth_lines = auth_log.read_text(encoding="utf-8", errors="replace").splitlines() if auth_log.exists() else []
    return sorted(parse_apache_lines(apache_lines) + parse_auth_lines(auth_lines), key=lambda row: row["timestamp"])
