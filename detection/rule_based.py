"""Simple explainable baseline rules for comparing against the ML model."""
from __future__ import annotations

def classify(row: dict) -> tuple[str, str]:
    """Return (attack label, human-readable risk) for one feature row."""
    if int(row.get("failed_count", 0)) > 5:
        return "brute_force", "High"
    if bool(int(row.get("contains_sqli_pattern", 0))):
        return "sql_injection", "High"
    if int(row.get("unique_paths", 0)) > 10:
        return "scanning", "Medium"
    return "normal", "Low"
