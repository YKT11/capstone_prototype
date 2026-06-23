"""Small DVWA client shared by the local training simulations.

This module must only be used against the deliberately vulnerable DVWA instance
installed inside the isolated training VM.  It never accepts arbitrary targets.
"""
from __future__ import annotations

import re
from typing import Optional

import requests

DEFAULT_BASE_URL = "http://localhost/DVWA"


class DVWASession:
    """Log into the local DVWA application and keep its cookies."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, source_ip: str = "127.0.0.1"):
        # Keeping this guard makes accidental use against a remote host harder.
        if not (base_url.startswith("http://localhost") or base_url.startswith("http://127.0.0.1")):
            raise ValueError("Simulators are restricted to localhost DVWA.")
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.headers = {"X-Forwarded-For": source_ip, "User-Agent": "CyberLab-Training/1.0"}

    @staticmethod
    def _token(html: str) -> Optional[str]:
        match = re.search(r"name=['\"]user_token['\"]\s+value=['\"]([^'\"]+)", html)
        return match.group(1) if match else None

    def login(self, username: str = "admin", password: str = "password") -> requests.Response:
        """Authenticate using DVWA's CSRF token-based login form."""
        login_page = self.session.get(f"{self.base_url}/login.php", headers=self.headers, timeout=10)
        login_page.raise_for_status()
        data = {"username": username, "password": password, "Login": "Login"}
        token = self._token(login_page.text)
        if token:
            data["user_token"] = token
        response = self.session.post(f"{self.base_url}/login.php", data=data, headers=self.headers, timeout=10)
        response.raise_for_status()
        return response

    def set_security_low(self) -> requests.Response:
        """Set the logged-in account's DVWA security level to low."""
        page = self.session.get(f"{self.base_url}/security.php", headers=self.headers, timeout=10)
        page.raise_for_status()
        data = {"security": "low", "seclev_submit": "Submit"}
        token = self._token(page.text)
        if token:
            data["user_token"] = token
        response = self.session.post(f"{self.base_url}/security.php", data=data, headers=self.headers, timeout=10)
        response.raise_for_status()
        return response

    def get(self, path: str, **kwargs: object) -> requests.Response:
        return self.session.get(f"{self.base_url}/{path.lstrip('/')}", headers=self.headers, timeout=10, **kwargs)
