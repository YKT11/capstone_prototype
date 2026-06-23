#!/usr/bin/env bash
# Install and verify a small local model. This needs internet only for first install/pull.
set -euo pipefail
MODEL_NAME="${MODEL_NAME:-llama3.2:3b}"
if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh
fi
sudo systemctl enable --now ollama 2>/dev/null || (ollama serve >/tmp/ollama.log 2>&1 &)
ollama pull "$MODEL_NAME"
for attempt in {1..15}; do
  if curl -fsS --max-time 3 http://localhost:11434/api/tags >/dev/null; then
    echo "Ollama is ready locally with $MODEL_NAME. No API key or per-message cost is used."
    exit 0
  fi
  sleep 2
done
echo "Ollama service did not respond on localhost:11434." >&2
exit 1
