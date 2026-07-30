"""FR-6: Train and tune Logistic Regression, Random Forest, and XGBoost.

Reads data/processed/customers_features.csv, does a stratified train/test
split, and tunes each model with RandomizedSearchCV (stratified 5-fold CV,
scoring on ROC-AUC). Saves each fitted pipeline plus the held-out test set
to models/ for evaluate_model.py to score independently.

Threshold note: models are trained here but NOT evaluated here at any
particular operating point -- see evaluate_model.py and the Phase 6
addendum for why 0.5 isn't the final threshold.
"""

import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.stats import loguniform, randint, uniform
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "customers_features.csv"
MODELS_DIR = PROJECT_ROOT / "models"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RANDOM_STATE = 42

CATEGORICAL_COLUMNS = [
    "gender", "multiple_lines", "internet_service", "online_security",
    "online_backup", "device_protection", "tech_support", "streaming_tv",
    "streaming_movies", "contract_type", "payment_method", "tenure_group",
    "revenue_category",
]
BOOLEAN_COLUMNS = [
    "senior_citizen", "partner", "dependents", "phone_service",
    "paperless_billing", "high_value_customer", "premium_customer",
    "autopay_customer",
]
NUMERIC_COLUMNS = ["tenure_months", "monthly_charges", "total_charges", "service_count"]


def load_dataset() -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(INPUT_PATH)
    y = df["churn"].astype(int)
    X = df[CATEGORICAL_COLUMNS + BOOLEAN_COLUMNS + NUMERIC_COLUMNS].copy()
    for col in BOOLEAN_COLUMNS:
        X[col] = X[col].astype(int)
    return X, y


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLUMNS),
            ("num", StandardScaler(), NUMERIC_COLUMNS),
            ("bool", "passthrough", BOOLEAN_COLUMNS),
        ]
    )


def get_model_configs(scale_pos_weight: float) -> dict:
    """Model + hyperparameter search space for each of the three candidates.

    Search spaces are intentionally modest (RandomizedSearchCV, n_iter=15) --
    this is a 7K-row dataset, diminishing returns hit fast, and the business
    layer (Phase 6) is the actual differentiator, not squeezing out another
    0.01 AUC here.
    """
    return {
        "logistic_regression": {
            "estimator": LogisticRegression(
                class_weight="balanced", max_iter=2000, random_state=RANDOM_STATE
            ),
            "param_distributions": {
                "classifier__C": loguniform(1e-3, 1e2),
            },
        },
        "random_forest": {
            "estimator": RandomForestClassifier(
                class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1
            ),
            "param_distributions": {
                "classifier__n_estimators": randint(100, 400),
                "classifier__max_depth": [None, 5, 10, 15, 20],
                "classifier__min_samples_leaf": randint(1, 8),
                "classifier__max_features": uniform(0.3, 0.7),
            },
        },
        "xgboost": {
            "estimator": XGBClassifier(
                scale_pos_weight=scale_pos_weight,
                eval_metric="logloss",
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
            "param_distributions": {
                "classifier__n_estimators": randint(100, 400),
                "classifier__max_depth": randint(3, 8),
                "classifier__learning_rate": loguniform(1e-2, 3e-1),
                "classifier__subsample": uniform(0.6, 0.4),
                "classifier__colsample_bytree": uniform(0.6, 0.4),
            },
        },
    }


def tune_model(name: str, config: dict, preprocessor: ColumnTransformer, X_train, y_train) -> Pipeline:
    pipeline = Pipeline([("preprocessor", preprocessor), ("classifier", config["estimator"])])
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    search = RandomizedSearchCV(
        pipeline,
        param_distributions=config["param_distributions"],
        n_iter=15,
        scoring="roc_auc",
        cv=cv,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    logger.info("Tuning %s ...", name)
    search.fit(X_train, y_train)
    logger.info("%s best CV ROC-AUC: %.4f, best params: %s", name, search.best_score_, search.best_params_)
    return search.best_estimator_


def main() -> None:
    X, y = load_dataset()
    logger.info("Loaded %d rows, target churn rate %.2f%%", len(X), 100 * y.mean())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )
    logger.info("Train: %d rows, Test: %d rows (stratified split)", len(X_train), len(X_test))

    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    logger.info("XGBoost scale_pos_weight (neg/pos ratio in train): %.3f", scale_pos_weight)

    preprocessor = build_preprocessor()
    model_configs = get_model_configs(scale_pos_weight)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    for name, config in model_configs.items():
        fitted_pipeline = tune_model(name, config, preprocessor, X_train, y_train)
        joblib.dump(fitted_pipeline, MODELS_DIR / f"{name}.pkl")
        logger.info("Saved %s.pkl", name)

    joblib.dump({"X_test": X_test, "y_test": y_test}, MODELS_DIR / "test_data.pkl")
    logger.info("Saved test_data.pkl (%d held-out rows) for evaluate_model.py", len(X_test))


if __name__ == "__main__":
    main()
