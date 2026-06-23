"""Instant deterministic explanations and a compact offline FAQ matcher."""
from __future__ import annotations

EXPLANATIONS = {
    "brute_force": "Possible brute-force behavior detected. Reason: {failed_count} failed login attempts were found from {source_ip} within {time_window} seconds. Risk Level: High. Recommended Action: Review this IP and consider rate-limiting or lockout policies.",
    "sql_injection": "Possible SQL injection attempt detected. Reason: the request to {request_path} contained a pattern resembling an SQL injection payload. Risk Level: High. Recommended Action: Review input validation and parameterized queries.",
    "scanning": "Possible scanning behavior detected. Reason: {source_ip} requested {unique_paths} distinct paths within {time_window} seconds. Risk Level: Medium. Recommended Action: Monitor this IP for further reconnaissance activity.",
    "normal": "No suspicious pattern detected. Activity is consistent with normal usage.",
}

def explain(label: str, row: dict | None = None) -> str:
    values = {"failed_count": 0, "source_ip": "unknown", "time_window": 60, "request_path": "unknown path", "unique_paths": 0}
    values.update(row or {})
    return EXPLANATIONS.get(label, EXPLANATIONS["normal"]).format(**values)

def answer_faq(question: str, context: str = "") -> str:
    """Useful safe response when the optional local model is offline."""
    lowered = question.lower()
    if "simulate" in lowered or "attack" in lowered:
        return "This prototype only simulates activity against localhost DVWA inside the isolated VM. Use the guides page for the four included local-only simulations; do not target other systems."
    if "brute" in lowered:
        return "Brute-force alerts occur when more than five failed-login events from one source IP appear in a 60-second window. " + context
    if "sql" in lowered or "injection" in lowered:
        return "SQL-injection alerts are raised when a request path contains common SQLi-like patterns. " + context
    return "The full local Ollama assistant is offline, so this deterministic explainer is answering instead. Ask about the included local simulations, an alert label, or detection features."
