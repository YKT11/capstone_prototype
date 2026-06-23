# CyberLab Training: AI-Assisted Cybersecurity Training Platform

CyberLab Training is a local-only capstone prototype for learning how hands-on DVWA activity becomes logs, labeled data, detections, and plain-language explanations. It combines an explainable rule engine, a Decision Tree, a Flask dashboard, and optional local Ollama assistance.

> **Safety:** DVWA is deliberately vulnerable. Run this project only in an isolated Kali VM using localhost/NAT or host-only networking. Never expose DVWA, Ollama, or the dashboard to a real network. Every guide command is restricted to `127.0.0.1` / local DVWA.

## Architecture

```text
Kali VM (DVWA + hands-on lab exercises) -> Logs -> Python Processing
  -> Detection (Rule-based + Decision Tree)
  -> AI Explanation (template + local Ollama model)
  -> Flask Dashboard
```

## Setup

Follow [the Kali VM guide](setup/kali_vm_setup_guide.md). Allocate **4 CPUs and 6–8 GB RAM**, because DVWA and a local language model run together.

```bash
# One-time setup inside the Kali VM
bash setup/provision.sh
bash setup/install_dvwa.sh
bash setup/install_ollama.sh
bash setup/branding/apply_branding.sh  # optional polish

# Start the dashboard (from the project root)
source venv/bin/activate
python dashboard/app.py
```

Open `http://localhost:5000`, then use the **Guides** page. You perform the controlled DVWA exercises manually; the dashboard explains the expected evidence and detection outcome.

After completing an exercise, use another terminal in the project root:

```bash
source venv/bin/activate
python lab/collect_logs.py
python processing/build_dataset.py
python detection/train.py
```

The Events page reads the rebuilt dataset. Reload it after training if it is already open.

## Hands-on workflow

The guides use real Kali methods, but only against local DVWA: browse normally to create a baseline, enumerate local DVWA paths, submit deliberately incorrect credentials to DVWA’s Brute Force page, and enter the supplied educational SQLi test input into DVWA’s SQL Injection page. They are not instructions for using tools against other hosts.

`python lab/run_all_simulations.py` remains available only as an optional automated demo-data generator for testing or presentations. It is not required for the learner-led workflow.

When manual activity has no simulator manifest, the dataset builder applies transparent threshold-based labels. This is an educational fallback, not production ground truth.

## Regenerate from scratch

Stop the dashboard, clear generated project artefacts, perform a new hands-on local exercise, then rebuild:

```bash
rm -f data/raw_logs/* data/labeled_dataset.csv models/* reports/*
python lab/collect_logs.py
python processing/build_dataset.py
python detection/train.py
```

## Folder map

- `setup/`: Kali, DVWA, Ollama, and optional branding scripts.
- `lab/`: local log collector, DVWA helper, and optional demo-data simulators.
- `processing/`: two-format parsing, rolling-window features, and dataset builder.
- `detection/`: threshold baseline, persistent Decision Tree, and evaluation command.
- `ai_explainer/`: deterministic templates plus local Ollama HTTP wrapper.
- `dashboard/`: Flask routes, templates, polling feed, and product styling.
- `data/`, `models/`, `reports/`: generated pipeline outputs.
- `tests/`: offline smoke tests.

## Local AI assistant

The assistant sends prompts only to a local Ollama server at `localhost:11434`; it uses no API key, cloud API, or per-message charge. Internet is needed only once to install Ollama and pull a model. To change models, run `ollama pull <model>` and set `MODEL_NAME` in `ai_explainer/ollama_client.py`. `phi3:mini` is a lighter low-RAM option. If Ollama is stopped or no model is pulled, the dashboard visibly switches to its template explainer instead of crashing.

## Limitations

This is an educational prototype, not a production SIEM or security control. Manual-lab labels are transparent heuristics unless an optional simulator manifest supplies ground truth. The local open model is less nuanced than a large hosted model. DVWA setup/log behavior varies slightly by release. The project deliberately excludes real-network scanning, real user telemetry, multi-host collection, and production hardening.

## Tests

```bash
python -m unittest discover -s tests -v
```

The smoke suite validates both log parsers, manual brute-force feature/lab labeling, rule detection, model persistence/prediction, and Ollama-unavailable behavior without making network requests.
