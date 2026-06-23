"""Standard-library smoke tests for the offline log-to-dashboard pipeline."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ai_explainer import ollama_client
from detection.ml_model import FEATURE_COLUMNS, load_model, predict, train_and_save
from detection.rule_based import classify
from processing.build_dataset import FIELDS, infer_lab_label
from processing.feature_extractor import add_features
from processing.log_parser import parse_apache_lines, parse_auth_lines


class PipelineSmokeTests(unittest.TestCase):
    def test_parsers_produce_rows(self):
        apache = parse_apache_lines(['10.10.10.10 - - [23/Jun/2026:12:00:00 +0000] "GET /DVWA/index.php HTTP/1.1" 200 123 "-" "test"'])
        auth = parse_auth_lines(['Jun 23 12:00:00 cyberlab dvwa-auth: Failed password for admin from 10.10.10.20 port 0 ssh2'], year=2026)
        self.assertEqual(apache[0]["source_ip"], "10.10.10.10")
        self.assertEqual(auth[0]["event_type"], "failed_login")

    def test_rule_engine_detects_bruteforce(self):
        self.assertEqual(classify({"failed_count": 6, "contains_sqli_pattern": 0, "unique_paths": 1}), ("brute_force", "High"))

    def test_manual_bruteforce_requests_receive_features_and_label(self):
        rows = [{"timestamp": f"2026-06-23 12:00:0{i}", "source_ip": "127.0.0.1", "event_type": "web_request", "request_path": "/DVWA/vulnerabilities/brute/?username=admin", "status_code": 200, "username": ""} for i in range(7)]
        featured = add_features(rows)
        self.assertEqual(featured[-1]["failed_count"], 7)
        self.assertEqual(infer_lab_label(featured[-1]), "brute_force")
        self.assertNotIn("username", FIELDS)

    def test_model_loads_and_predicts(self):
        import pandas as pd
        import detection.ml_model as module
        with tempfile.TemporaryDirectory() as folder:
            folder_path = Path(folder); fixture = folder_path / "dataset.csv"
            records = []
            examples = [("normal", [200, 0, 2, 2, 0, 60]), ("brute_force", [401, 8, 9, 1, 0, 60]), ("sql_injection", [200, 0, 3, 1, 1, 60]), ("scanning", [404, 0, 15, 12, 0, 60])]
            for label, values in examples:
                for _ in range(5): records.append(dict(zip(FEATURE_COLUMNS, values), label=label))
            pd.DataFrame(records).to_csv(fixture, index=False)
            with patch.object(module, "MODEL_PATH", folder_path / "model.joblib"), patch.object(module, "COLUMNS_PATH", folder_path / "columns.json"):
                model, _, _ = train_and_save(fixture)
                self.assertIsNotNone(model)
                self.assertEqual(predict(dict(zip(FEATURE_COLUMNS, [401, 8, 9, 1, 0, 60])), load_model()), "brute_force")

    def test_ollama_failure_returns_none(self):
        import requests
        with patch.object(ollama_client.requests, "post", side_effect=requests.ConnectionError("offline")):
            self.assertIsNone(ollama_client.ask_assistant("hello"))


if __name__ == "__main__":
    unittest.main()
