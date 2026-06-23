"""Optional demo-data generator; hands-on exercises are the primary workflow."""
from __future__ import annotations
import time
import shutil
from pathlib import Path
import sys
if __package__ is None: sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab import simulate_bruteforce, simulate_normal, simulate_scanning, simulate_sqli

def main() -> None:
    results = []
    for name, action in [("normal", simulate_normal.run), ("brute force", simulate_bruteforce.run), ("SQL injection", simulate_sqli.run), ("scanning", simulate_scanning.run)]:
        results.append((name, action()))
        time.sleep(1)
    print("Optional automated-demo summary:")
    for name, count in results:
        print(f"- {name}: {count} requests/events")
    source_log = Path("/var/log/apache2/access.log")
    destination = Path(__file__).resolve().parents[1] / "data" / "raw_logs" / "access.log"
    if source_log.exists():
        shutil.copy2(source_log, destination)
        print(f"Copied Apache access log to {destination}.")
    else:
        print("Apache access.log was not found; only auth-style events were generated.")

if __name__ == "__main__":
    main()
