"""FR-2: Data quality checks against the loaded customers table.

Run after load_data.py. Reports missing values, duplicate customer IDs,
blank/null total_charges, unexpected categorical values, and dtypes -- a
console summary a human can read before preprocessing.py decides how to
fix anything found here.
"""

import logging

import pandas as pd

from db import get_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

EXPECTED_CATEGORIES = {
    "gender": {"Male", "Female"},
    "multiple_lines": {"Yes", "No", "No phone service"},
    "internet_service": {"DSL", "Fiber optic", "No"},
    "online_security": {"Yes", "No", "No internet service"},
    "online_backup": {"Yes", "No", "No internet service"},
    "device_protection": {"Yes", "No", "No internet service"},
    "tech_support": {"Yes", "No", "No internet service"},
    "streaming_tv": {"Yes", "No", "No internet service"},
    "streaming_movies": {"Yes", "No", "No internet service"},
    "contract_type": {"Month-to-month", "One year", "Two year"},
    "payment_method": {
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    },
}

NUMERIC_COLUMNS = ["tenure_months", "monthly_charges", "total_charges"]


def load_customers() -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql("SELECT * FROM customers", engine)


def check_missing_values(df: pd.DataFrame) -> None:
    missing = df.isna().sum()
    missing = missing[missing > 0]
    if missing.empty:
        logger.info("No missing values in any column.")
    else:
        for col, count in missing.items():
            logger.warning("Column '%s' has %d missing value(s).", col, count)


def check_duplicate_ids(df: pd.DataFrame) -> None:
    dupes = df["customer_id"].duplicated().sum()
    if dupes == 0:
        logger.info("No duplicate customer_id values.")
    else:
        logger.warning("%d duplicate customer_id value(s) found.", dupes)


def check_blank_total_charges(df: pd.DataFrame) -> None:
    blank = df[df["total_charges"].isna()]
    logger.info("%d row(s) with null total_charges.", len(blank))
    if not blank.empty:
        non_zero_tenure = blank[blank["tenure_months"] != 0]
        if non_zero_tenure.empty:
            logger.info("All null total_charges rows have tenure_months = 0, as expected.")
        else:
            logger.warning(
                "%d null total_charges row(s) have tenure_months != 0 -- unexpected.",
                len(non_zero_tenure),
            )


def check_categorical_values(df: pd.DataFrame) -> None:
    for col, expected in EXPECTED_CATEGORIES.items():
        actual = set(df[col].dropna().unique())
        unexpected = actual - expected
        if unexpected:
            logger.warning("Column '%s' has unexpected value(s): %s", col, unexpected)
        else:
            logger.info("Column '%s' matches expected categories.", col)


def check_dtypes(df: pd.DataFrame) -> None:
    for col in NUMERIC_COLUMNS:
        if not pd.api.types.is_numeric_dtype(df[col]):
            logger.warning("Column '%s' is not numeric (dtype=%s).", col, df[col].dtype)
        else:
            logger.info("Column '%s' dtype OK (%s).", col, df[col].dtype)


def main() -> None:
    df = load_customers()
    logger.info("Loaded %d rows from customers for validation.", len(df))

    check_missing_values(df)
    check_duplicate_ids(df)
    check_blank_total_charges(df)
    check_categorical_values(df)
    check_dtypes(df)

    logger.info("Validation complete.")


if __name__ == "__main__":
    main()
