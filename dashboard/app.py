"""Flask application for the local CyberLab training platform."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
from flask import Flask, jsonify, render_template, request, send_from_directory
from ai_explainer.explainer import answer_faq, explain
from ai_explainer.ollama_client import ask_assistant
from detection.ml_model import load_model, predict
from detection.rule_based import classify

DATASET = ROOT / "data" / "labeled_dataset.csv"
METRICS = ROOT / "reports" / "metrics.json"

def rows() -> list[dict]:
    if not DATASET.exists(): return []
    return pd.read_csv(DATASET).fillna("").to_dict(orient="records")

def enrich(row: dict) -> dict:
    rule_label, risk = classify(row)
    try: ml_label = predict(row, load_model())
    except (FileNotFoundError, ValueError): ml_label = row.get("label", "normal")
    return {**row, "rule_label": rule_label, "ml_label": ml_label, "risk": risk, "explanation": explain(ml_label, row), "disagreement": rule_label != ml_label}

def create_app() -> Flask:
    app = Flask(__name__)
    @app.get("/")
    def index():
        events = [enrich(row) for row in rows()]
        counts = pd.Series([event["ml_label"] for event in events]).value_counts().to_dict() if events else {}
        metrics = json.loads(METRICS.read_text()) if METRICS.exists() else {}
        return render_template("index.html", events=events[-50:], counts=counts, accuracy=metrics.get("accuracy"))
    @app.get("/api/latest-events")
    def latest_events(): return jsonify([enrich(row) for row in rows()[-50:]])
    @app.get("/guides")
    def guides(): return render_template("guides.html")
    @app.get("/logs")
    def logs():
        label = request.args.get("label", "")
        listed = rows(); listed = [row for row in listed if row.get("label") == label] if label else listed
        return render_template("logs.html", rows=listed, selected=label)
    @app.get("/alerts")
    def alerts(): return render_template("alerts.html", alerts=[enrich(row) for row in rows()])
    @app.route("/assistant", methods=["GET", "POST"])
    def assistant():
        response = None; offline = False; question = ""
        if request.method == "POST":
            question = request.form.get("question", "").strip()
            context = request.form.get("context", "")
            response = ask_assistant(question, context)
            offline = response is None
            response = response or answer_faq(question, context)
        return render_template("assistant.html", response=response, offline=offline, question=question)
    @app.get("/model-eval")
    def model_eval():
        metrics = json.loads(METRICS.read_text()) if METRICS.exists() else None
        return render_template("model_eval.html", metrics=metrics)
    @app.get("/reports/<path:filename>")
    def report_file(filename: str):
        return send_from_directory(ROOT / "reports", filename)
    return app

if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=True)
