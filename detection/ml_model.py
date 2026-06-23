"""Decision Tree training, persistence, and single-row prediction utilities."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "labeled_dataset.csv"
MODEL_PATH = ROOT / "models" / "decision_tree.joblib"
COLUMNS_PATH = ROOT / "models" / "feature_columns.json"
FEATURE_COLUMNS = ["status_code", "failed_count", "request_count", "unique_paths", "contains_sqli_pattern", "time_window"]


def _dataset(dataset_path: Path = DATASET) -> pd.DataFrame:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}. Run processing/build_dataset.py first.")
    frame = pd.read_csv(dataset_path)
    if frame.empty or "label" not in frame:
        raise ValueError("Dataset must contain non-empty labeled rows.")
    missing = set(FEATURE_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing features: {sorted(missing)}")
    return frame


def train_and_save(dataset_path: Path = DATASET, max_depth: int = 6):
    """Train a deterministic tree and persist both estimator and feature order.

    A stratified 80/20 split is returned for evaluation. Each class needs at
    least two examples, which the supplied simulations produce.
    """
    frame = _dataset(dataset_path)
    X, y = frame[FEATURE_COLUMNS], frame["label"]
    if y.nunique() < 2 or y.value_counts().min() < 2:
        raise ValueError("Need at least two examples of every class to train/test split.")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    model.fit(X_train, y_train)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    COLUMNS_PATH.write_text(json.dumps(FEATURE_COLUMNS, indent=2), encoding="utf-8")
    return model, X_test, y_test


def load_model(model_path: Path | None = None):
    model_path = model_path or MODEL_PATH
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}. Run detection/train.py first.")
    return joblib.load(model_path)


def predict(row_features: dict, model=None) -> str:
    """Predict an attack label from a dictionary containing the six features."""
    model = model or load_model()
    frame = pd.DataFrame([{name: row_features.get(name, 0) for name in FEATURE_COLUMNS}])
    return str(model.predict(frame)[0])
