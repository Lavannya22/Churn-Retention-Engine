"""FR-2: Apply cleaning decisions and write the cleaned dataset.

Run after load_data.py and validation.py. Cleaning decisions made here:

- total_charges is NULL only for tenure_months = 0 customers (confirmed in
  validation.py) -- they haven't been billed yet, so we set it to 0 rather
  than dropping the row. Dropping would lose 11 real customers over a
  mechanical gap, not a data quality problem.
- Categorical text columns are stripped of surrounding whitespace, defensively
  (the source CSV has none, but this guards against a future re-export that
  does).
- Duplicate customer_id rows are dropped, keeping the first occurrence,
  defensively (none currently exist in this dataset -- confirmed in
  validation.py).

Output: data/processed/customers_clean.csv, plus the total_charges fix is
also applied back to the Postgres customers table directly (Phase 3+
query that table, not the CSV, so the fix needs to live there too).
"""

import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db import get_engine

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "customers_clean.csv"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CATEGORICAL_TEXT_COLUMNS = [
    "gender",
    "multiple_lines",
    "internet_service",
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_tv",
    "streaming_movies",
    "contract_type",
    "payment_method",
]


def load_customers() -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql("SELECT * FROM customers", engine)


def persist_total_charges_fix() -> None:
    """Apply the same total_charges = 0 fix directly in Postgres.

    Phase 3+ query the customers table directly, so the cleaning decision
    made here needs to live in the database, not just in the CSV export.
    """
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "UPDATE customers SET total_charges = 0 "
                "WHERE total_charges IS NULL AND tenure_months = 0"
            )
        )
        logger.info("Updated %d row(s) in Postgres customers table.", result.rowcount)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)

    zero_tenure_mask = df["total_charges"].isna() & (df["tenure_months"] == 0)
    df.loc[zero_tenure_mask, "total_charges"] = 0.0
    logger.info("Filled total_charges = 0 for %d zero-tenure customer(s).", zero_tenure_mask.sum())

    for col in CATEGORICAL_TEXT_COLUMNS:
        df[col] = df[col].str.strip()

    df = df.drop_duplicates(subset="customer_id", keep="first")
    dropped = before - len(df)
    if dropped:
        logger.info("Dropped %d duplicate customer_id row(s).", dropped)

    return df


def main() -> None:
    df = load_customers()
    logger.info("Loaded %d rows from customers for preprocessing.", len(df))

    df = clean(df)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    logger.info("Wrote %d cleaned rows to %s", len(df), OUTPUT_PATH)

    persist_total_charges_fix()


if __name__ == "__main__":
    main()
