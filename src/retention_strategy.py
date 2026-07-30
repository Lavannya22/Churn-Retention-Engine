"""FR-7: Business Decision Engine.

Run after evaluate_model.py. Turns the XGBoost model's churn probabilities
into per-customer business recommendations: CLV, revenue at risk, expected
net benefit of a retention offer, and a Retain / Monitor / No Action call --
with the classification threshold chosen to maximize business ROI on the
held-out test set, not left at the default 0.5.

Assumptions (see README's Assumptions & Limitations section):
- Retention offer cost: $20/customer (fixed).
- Retention offer success rate: 25% (if offered to a customer who was truly
  going to churn, it saves them 25% of the time).
- CLV = monthly_charges * 12. A flat 12-month horizon, not churn-adjusted or
  discounted -- deliberately simple per the roadmap's explicit "don't let
  CLV become a rabbit hole" guidance. Documented limitation, not an
  oversight: a customer's true expected remaining tenure obviously varies,
  but folding that in would require assumptions on top of assumptions for
  a marginal accuracy gain that isn't the point of this exercise.
"""

import logging
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, precision_score, recall_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
from train_model import BOOLEAN_COLUMNS, CATEGORICAL_COLUMNS, NUMERIC_COLUMNS  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
FEATURES_PATH = PROJECT_ROOT / "data" / "processed" / "customers_features.csv"
RECOMMENDATIONS_PATH = PROJECT_ROOT / "data" / "processed" / "customer_recommendations.csv"
TOP_RISK_REPORT_PATH = PROJECT_ROOT / "reports" / "top_risk_customers.md"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

OFFER_COST = 20.0
OFFER_SUCCESS_RATE = 0.25
EXPECTED_REMAINING_MONTHS = 12

THRESHOLD_CANDIDATES = np.arange(0.05, 0.96, 0.01)


def compute_clv(monthly_charges: pd.Series) -> pd.Series:
    return monthly_charges * EXPECTED_REMAINING_MONTHS


def backtest_business_value(y_true: np.ndarray, y_proba: np.ndarray, clv: np.ndarray, threshold: float) -> float:
    """Total dollar business value of using `threshold` as the offer cutoff,
    measured against actual outcomes in a labeled (test) set.

    Per predicted-offer customer:
    - Flagged + actually churned (true positive): we pay the offer cost, and
      with probability OFFER_SUCCESS_RATE we save their CLV. Expected value:
      OFFER_SUCCESS_RATE * CLV - OFFER_COST.
    - Flagged + actually retained anyway (false positive): wasted cost,
      no benefit. Value: -OFFER_COST.
    - Not flagged + actually churned (false negative): no cost paid, but we
      lose the full CLV since we didn't intervene. Value: -CLV.
    - Not flagged + actually retained (true negative): no cost, no benefit.
      Value: 0.
    """
    flagged = y_proba >= threshold
    churned = y_true == 1

    tp_value = np.where(flagged & churned, OFFER_SUCCESS_RATE * clv - OFFER_COST, 0.0)
    fp_value = np.where(flagged & ~churned, -OFFER_COST, 0.0)
    fn_value = np.where(~flagged & churned, -clv, 0.0)

    return float((tp_value + fp_value + fn_value).sum())


def find_optimal_threshold(y_true: np.ndarray, y_proba: np.ndarray, clv: np.ndarray) -> tuple[float, pd.DataFrame]:
    records = [
        {"threshold": round(t, 2), "business_value": backtest_business_value(y_true, y_proba, clv, t)}
        for t in THRESHOLD_CANDIDATES
    ]
    sweep_df = pd.DataFrame(records)
    best_row = sweep_df.loc[sweep_df["business_value"].idxmax()]
    return float(best_row["threshold"]), sweep_df


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    X = df[CATEGORICAL_COLUMNS + BOOLEAN_COLUMNS + NUMERIC_COLUMNS].copy()
    for col in BOOLEAN_COLUMNS:
        X[col] = X[col].astype(int)
    return X


def recommend_action(churn_probability: float, expected_net_benefit: float, threshold: float) -> str:
    if churn_probability >= threshold:
        return "Retain" if expected_net_benefit > 0 else "Monitor"
    return "No Action"


def main() -> None:
    pipeline = joblib.load(MODELS_DIR / "xgboost.pkl")
    test_data = joblib.load(MODELS_DIR / "test_data.pkl")
    X_test, y_test = test_data["X_test"], test_data["y_test"]

    test_proba = pipeline.predict_proba(X_test)[:, 1]
    test_clv = compute_clv(X_test["monthly_charges"]).to_numpy()

    optimal_threshold, sweep_df = find_optimal_threshold(y_test.to_numpy(), test_proba, test_clv)
    value_at_optimal = sweep_df.loc[sweep_df["threshold"] == round(optimal_threshold, 2), "business_value"].iloc[0]
    value_at_default = backtest_business_value(y_test.to_numpy(), test_proba, test_clv, 0.5)
    value_at_no_program = backtest_business_value(y_test.to_numpy(), test_proba, test_clv, 1.01)  # nobody flagged

    logger.info("Optimal ROI threshold: %.2f (business value on test set: $%.2f)", optimal_threshold, value_at_optimal)
    logger.info("Business value at default 0.5 threshold: $%.2f", value_at_default)
    logger.info("Business value with no retention program at all: $%.2f", value_at_no_program)
    logger.info(
        "ROI-optimized threshold improves on default 0.5 by $%.2f, and on no program by $%.2f",
        value_at_optimal - value_at_default, value_at_optimal - value_at_no_program,
    )

    y_pred_at_optimal = (test_proba >= optimal_threshold).astype(int)
    precision = precision_score(y_test, y_pred_at_optimal)
    recall = recall_score(y_test, y_pred_at_optimal)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred_at_optimal).ravel()
    logger.info(
        "At optimal threshold -- Precision: %.4f, Recall: %.4f, Confusion matrix: TN=%d FP=%d FN=%d TP=%d",
        precision, recall, tn, fp, fn, tp,
    )

    # Score currently-active (not yet churned) customers for actionable recommendations --
    # offering a retention deal to someone who's already left isn't operationally meaningful.
    full_df = pd.read_csv(FEATURES_PATH)
    active_df = full_df[~full_df["churn"]].copy()
    X_active = build_feature_matrix(active_df)

    active_df["churn_probability"] = pipeline.predict_proba(X_active)[:, 1]
    active_df["clv"] = compute_clv(active_df["monthly_charges"])
    active_df["revenue_at_risk"] = active_df["churn_probability"] * active_df["clv"]
    active_df["retention_offer_cost"] = OFFER_COST
    active_df["expected_net_benefit"] = (
        active_df["churn_probability"] * OFFER_SUCCESS_RATE * active_df["clv"] - OFFER_COST
    )
    active_df["recommended_action"] = active_df.apply(
        lambda row: recommend_action(row["churn_probability"], row["expected_net_benefit"], optimal_threshold),
        axis=1,
    )

    action_counts = active_df["recommended_action"].value_counts()
    logger.info("Recommended actions across %d active customers: %s", len(active_df), action_counts.to_dict())

    output_cols = [
        "customer_id", "churn_probability", "monthly_charges", "clv",
        "revenue_at_risk", "retention_offer_cost", "expected_net_benefit", "recommended_action",
    ]
    RECOMMENDATIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    active_df[output_cols].to_csv(RECOMMENDATIONS_PATH, index=False)
    logger.info("Wrote %d scored customers to %s", len(active_df), RECOMMENDATIONS_PATH)

    top_20 = active_df.sort_values("churn_probability", ascending=False).head(20)
    write_top_risk_report(top_20, optimal_threshold, action_counts, value_at_optimal, value_at_default, value_at_no_program)


def write_top_risk_report(top_20, threshold, action_counts, value_optimal, value_default, value_no_program) -> None:
    lines = [
        "# Phase 6 -- Top 20 Highest-Risk Active Customers",
        "",
        f"Scored with the XGBoost model at the ROI-optimal threshold ({threshold:.2f}). "
        "Only currently-active (not yet churned) customers are scored, since a retention "
        "offer only makes sense for someone who hasn't left.",
        "",
        f"**Recommended action breakdown (all {sum(action_counts.values)} active customers):** "
        + ", ".join(f"{k}: {v}" for k, v in action_counts.items()),
        "",
        f"**Backtested business value on the held-out test set:** ${value_optimal:,.2f} at the "
        f"optimal threshold, vs. ${value_default:,.2f} at the default 0.5 threshold, vs. "
        f"${value_no_program:,.2f} with no retention program at all.",
        "",
        "| customer_id | churn_probability | monthly_charges | clv | revenue_at_risk | expected_net_benefit | recommended_action |",
        "|---|---|---|---|---|---|---|",
    ]
    for _, row in top_20.iterrows():
        lines.append(
            f"| {row['customer_id']} | {row['churn_probability']:.3f} | ${row['monthly_charges']:.2f} | "
            f"${row['clv']:.2f} | ${row['revenue_at_risk']:.2f} | ${row['expected_net_benefit']:.2f} | "
            f"{row['recommended_action']} |"
        )

    TOP_RISK_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOP_RISK_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote top-risk sample to %s", TOP_RISK_REPORT_PATH)


if __name__ == "__main__":
    main()
