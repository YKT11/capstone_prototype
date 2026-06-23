"""Train the Decision Tree and write metrics plus a confusion-matrix image."""
from __future__ import annotations

import json
from pathlib import Path
import sys
if __package__ is None: sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support

from detection.ml_model import ROOT, train_and_save
from detection.rule_based import classify


def main() -> dict:
    model, X_test, y_test = train_and_save()
    predicted = model.predict(X_test)
    labels = sorted(set(y_test) | set(predicted))
    precision, recall, _, _ = precision_recall_fscore_support(y_test, predicted, average="weighted", zero_division=0)
    rule_predictions = [classify(row.to_dict())[0] for _, row in X_test.iterrows()]
    metrics = {"accuracy": accuracy_score(y_test, predicted), "precision_weighted": precision, "recall_weighted": recall, "rule_based_accuracy": accuracy_score(y_test, rule_predictions), "test_rows": int(len(y_test)), "labels": labels}

    reports = ROOT / "reports"; reports.mkdir(exist_ok=True)
    (reports / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    matrix = confusion_matrix(y_test, predicted, labels=labels)
    plt.figure(figsize=(7, 5)); sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
    plt.xlabel("Predicted"); plt.ylabel("Actual"); plt.title("Decision Tree Confusion Matrix"); plt.tight_layout()
    plt.savefig(reports / "confusion_matrix.png", dpi=150); plt.close()
    print(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    main()
