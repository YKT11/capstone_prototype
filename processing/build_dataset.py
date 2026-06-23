"""Build the labeled CSV from raw logs and simulator ground-truth manifest."""
from __future__ import annotations

import csv
from pathlib import Path
import sys
if __package__ is None: sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from processing.feature_extractor import add_features
from processing.log_parser import parse_logs

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw_logs"
OUTPUT = ROOT / "data" / "labeled_dataset.csv"
FIELDS = ["timestamp", "source_ip", "event_type", "request_path", "status_code", "failed_count", "request_count", "unique_paths", "contains_sqli_pattern", "time_window", "label"]


def load_manifest(path: Path = RAW / "simulation_manifest.csv") -> dict[str, str]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["source_ip"]: row["label"] for row in csv.DictReader(handle)}


def infer_lab_label(row: dict) -> str:
    """Provide transparent labels for manual DVWA exercises without a manifest.

    Simulator manifests remain the preferred ground truth.  This fallback is
    deliberately simple and mirrors the documented detection thresholds, so
    a learner can understand why a manually generated event was labeled.
    """
    if int(row.get("failed_count", 0)) > 5:
        return "brute_force"
    if int(row.get("contains_sqli_pattern", 0)):
        return "sql_injection"
    if int(row.get("unique_paths", 0)) > 10:
        return "scanning"
    return "normal"


def build_dataset(raw_dir: Path = RAW, output: Path = OUTPUT) -> list[dict]:
    """Parse available logs, add features, label known training IPs, and save CSV."""
    labels = load_manifest(raw_dir / "simulation_manifest.csv")
    rows = add_features(parse_logs(raw_dir / "access.log", raw_dir / "auth.log"))
    for row in rows:
        row["label"] = labels.get(row["source_ip"], infer_lab_label(row))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        # Keep username in memory for investigations, but write exactly the
        # specified labeled-dataset schema.
        writer.writerows({field: row.get(field, "") for field in FIELDS} for row in rows)
    return rows


if __name__ == "__main__":
    result = build_dataset()
    print(f"Wrote {len(result)} labeled rows to {OUTPUT}")
