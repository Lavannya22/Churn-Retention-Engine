"""FR-6: Evaluate the three trained models on the held-out test set.

Run after train_model.py. Loads each saved pipeline plus the held-out test
set, and reports Accuracy, Precision, Recall, F1, ROC-AUC, and a confusion
matrix -- all at the DEFAULT 0.5 THRESHOLD, per the roadmap's explicit
instruction.

Threshold note: this is intentionally incomplete. 0.5 tells you about model
QUALITY (via ROC-AUC, which is threshold-independent), not the operating
point you'd actually use. Phase 6's retention_strategy.py picks the real
threshold by sweeping candidate probabilities for business ROI, then an
addendum gets added below the comparison table this script produces.
"""

import logging
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
REPORT_PATH = PROJECT_ROOT / "reports" / "model_comparison.md"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MODEL_NAMES = ["logistic_regression", "random_forest", "xgboost"]
MODEL_DISPLAY_NAMES = {
    "logistic_regression": "Logistic Regression",
    "random_forest": "Random Forest",
    "xgboost": "XGBoost",
}


def evaluate_model(name: str, X_test, y_test) -> dict:
    pipeline = joblib.load(MODELS_DIR / f"{name}.pkl")
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= 0.5).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    return {
        "model": name,
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba),
        "tn": tn, "fp": fp, "fn": fn, "tp": tp,
    }


def format_report(results: list[dict], n_test: int, churn_rate: float) -> str:
    lines = [
        "# Phase 5 -- Model Comparison (default 0.5 threshold)",
        "",
        f"Evaluated on the held-out test set ({n_test} customers, {churn_rate:.2f}% actual churn "
        "rate), which none of the three models saw during training or hyperparameter tuning.",
        "",
        "**Threshold note:** these metrics use the default 0.5 probability threshold, as "
        "instructed for Phase 5 -- they measure model quality (ROC-AUC is threshold-independent), "
        "not the operating point that will actually be used. Phase 6 picks the real threshold by "
        "business ROI; see the addendum at the bottom of this file once that's done.",
        "",
        "| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {MODEL_DISPLAY_NAMES[r['model']]} | {r['accuracy']:.4f} | {r['precision']:.4f} | "
            f"{r['recall']:.4f} | {r['f1']:.4f} | {r['roc_auc']:.4f} |"
        )

    lines += ["", "## Confusion matrices (rows = actual, cols = predicted; 0.5 threshold)", ""]
    for r in results:
        lines += [
            f"**{MODEL_DISPLAY_NAMES[r['model']]}**",
            "",
            "|  | Predicted: No Churn | Predicted: Churn |",
            "|---|---|---|",
            f"| Actual: No Churn | {r['tn']} | {r['fp']} |",
            f"| Actual: Churn | {r['fn']} | {r['tp']} |",
            "",
        ]

    return "\n".join(lines)


def main() -> None:
    test_data = joblib.load(MODELS_DIR / "test_data.pkl")
    X_test, y_test = test_data["X_test"], test_data["y_test"]
    logger.info("Loaded test set: %d rows, %.2f%% churn", len(X_test), 100 * y_test.mean())

    results = [evaluate_model(name, X_test, y_test) for name in MODEL_NAMES]

    for r in results:
        logger.info(
            "%s -- Accuracy: %.4f, Precision: %.4f, Recall: %.4f, F1: %.4f, ROC-AUC: %.4f",
            MODEL_DISPLAY_NAMES[r["model"]], r["accuracy"], r["precision"], r["recall"], r["f1"], r["roc_auc"],
        )

    report = format_report(results, len(X_test), 100 * y_test.mean())
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    logger.info("Wrote comparison report to %s", REPORT_PATH)


if __name__ == "__main__":
    main()
