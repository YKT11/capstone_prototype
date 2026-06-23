"""Copy local Apache logs into the project after a hands-on lab exercise.

This does not generate any traffic.  It is the bridge between a learner's
manual DVWA activity and the processing/detection pipeline.
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APACHE_ACCESS_LOG = Path("/var/log/apache2/access.log")
DESTINATION = ROOT / "data" / "raw_logs" / "access.log"


def collect() -> Path:
    """Copy the local Apache access log after confirming it is available."""
    if not APACHE_ACCESS_LOG.exists():
        raise FileNotFoundError(
            f"Apache log not found at {APACHE_ACCESS_LOG}. "
            "Check that Apache is running and DVWA was installed."
        )
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(APACHE_ACCESS_LOG, DESTINATION)
    return DESTINATION


if __name__ == "__main__":
    path = collect()
    print(f"Copied local Apache access log to {path}")
