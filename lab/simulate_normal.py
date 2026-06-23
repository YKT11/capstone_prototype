"""Generate benign browsing activity against local DVWA."""
from __future__ import annotations
import random
import sys
import time
from pathlib import Path
if __package__ is None: sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab.dvwa_session import DVWASession
from lab.simulation_common import record_phase

SOURCE_IP = "10.10.10.10"

def run(requests_count: int = 50) -> int:
    record_phase(SOURCE_IP, "normal")
    client = DVWASession(source_ip=SOURCE_IP)
    client.login(); client.set_security_low()
    paths = ["index.php", "instructions.php", "security.php", "vulnerabilities/sqli/?id=1&Submit=Submit"]
    for _ in range(requests_count):
        client.get(random.choice(paths))
        time.sleep(random.uniform(0.03, 0.12))
    return requests_count

if __name__ == "__main__":
    print(f"Generated {run()} normal requests.")
