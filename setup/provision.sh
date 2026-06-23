#!/usr/bin/env bash
# Idempotent project bootstrap for the isolated Kali VM.
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip git
python3 -m venv "$PROJECT_ROOT/venv"
"$PROJECT_ROOT/venv/bin/python" -m pip install --upgrade pip
"$PROJECT_ROOT/venv/bin/python" -m pip install -r "$PROJECT_ROOT/requirements.txt"
echo "Provisioning complete. Activate with: source $PROJECT_ROOT/venv/bin/activate"
