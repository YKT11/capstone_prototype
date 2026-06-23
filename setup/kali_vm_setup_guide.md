# Kali VM setup guide

Use the official Kali Linux VirtualBox or VMware image from kali.org. Allocate **4 CPUs and 6–8 GB RAM** (the local model runs beside DVWA), enable enough disk space for the model, then import the appliance.

Use **NAT or host-only networking only**. Do not use bridged networking, port forwarding, or an untrusted network while DVWA is running. Log in with the credentials provided by the current official Kali image, then clone/copy this project into the VM.

From the project root run:

```bash
bash setup/provision.sh
bash setup/install_dvwa.sh
bash setup/install_ollama.sh
bash setup/branding/apply_branding.sh  # optional
```

After DVWA installation, visit `http://localhost/DVWA/setup.php` and use **Create / Reset Database**. This is the one DVWA-version-dependent initialization action. The default DVWA account is `admin` / `password`; change it outside a classroom lab.

For hands-on exercises, Apache records local DVWA requests in `access.log` (normally from `127.0.0.1`). After each exercise run `python lab/collect_logs.py`, `python processing/build_dataset.py`, and `python detection/train.py`. Optional simulators use `X-Forwarded-For` training addresses; Apache's local-only `remoteip` configuration supports those demo runs. Never configure this trust boundary on an internet-facing server.

Ollama downloads `llama3.2:3b` once. For a lower-RAM VM use `MODEL_NAME=phi3:mini bash setup/install_ollama.sh`, then update `MODEL_NAME` in `ai_explainer/ollama_client.py`.

DVWA is deliberately vulnerable. Keep DVWA, Ollama, and every simulation on localhost/NAT isolation; never point scripts at other hosts or expose ports 80/5000/11434.
