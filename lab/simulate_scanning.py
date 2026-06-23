"""Generate rapid path enumeration against local DVWA only."""
from __future__ import annotations
import sys
from pathlib import Path
if __package__ is None: sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab.dvwa_session import DVWASession
from lab.simulation_common import record_phase

SOURCE_IP = "10.10.10.40"
PATHS = ["index.php", "login.php", "security.php", "instructions.php", "vulnerabilities/brute/", "vulnerabilities/sqli/", "vulnerabilities/xss_r/", "vulnerabilities/exec/", "does-not-exist-a", "admin", "robots.txt", "phpinfo.php", "missing-page"]

def run() -> int:
    record_phase(SOURCE_IP, "scanning")
    client = DVWASession(source_ip=SOURCE_IP)
    client.login(); client.set_security_low()
    for path in PATHS:
        client.get(path)
    return len(PATHS)

if __name__ == "__main__":
    print(f"Generated {run()} local scanning-like requests.")
