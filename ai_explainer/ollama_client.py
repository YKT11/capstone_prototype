"""Minimal client for an Ollama model served locally, with no cloud fallback."""
from __future__ import annotations
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"

def ask_assistant(prompt: str, context: str = "") -> str | None:
    full_prompt = f"{context}\n\nUser question: {prompt}" if context else prompt
    try:
        response = requests.post(OLLAMA_URL, json={"model": MODEL_NAME, "prompt": full_prompt, "stream": False}, timeout=30)
        response.raise_for_status()
        return response.json().get("response", "").strip() or None
    except (requests.RequestException, ValueError):
        return None
