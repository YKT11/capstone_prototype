"""Generate repeated failed requests only against the local DVWA brute-force page."""
from __future__ import annotations
import time
import sys
from pathlib import Path
if __package__ is None: sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab.dvwa_session import DVWASession
from lab.simulation_common import record_phase, write_auth_failure

SOURCE_IP = "10.10.10.20"

def run(attempts: int = 20) -> int:
    record_phase(SOURCE_IP, "brute_force")
    client = DVWASession(source_ip=SOURCE_IP)
    client.login(); client.set_security_low()
    for _ in range(attempts):
        client.get("vulnerabilities/brute/", params={"username": "admin", "password": "wrong-password", "Login": "Login"})
        # Deterministic second log source: DVWA does not natively create auth.log.
        write_auth_failure(SOURCE_IP)
        time.sleep(0.03)
    return attempts

if __name__ == "__main__":
    print(f"Generated {run()} local brute-force attempts.")
