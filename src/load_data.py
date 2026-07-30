"""FR-1: Load the raw Telco Customer Churn CSV into PostgreSQL.

Reads data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv, coerces each column to
the type the customers table (database/schema.sql) expects, and loads it.
Re-runnable: truncates customers before inserting so re-running this script
doesn't create duplicates or fail on the primary key.
"""

import logging
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db import get_engine

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_CSV_PATH = PROJECT_ROOT / "data" / "raw" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Maps raw CSV column names to customers table column names.
COLUMN_MAP = {
    "customerID": "customer_id",
    "gender": "gender",
    "SeniorCitizen": "senior_citizen",
    "Partner": "partner",
    "Dependents": "dependents",
    "tenure": "tenure_months",
    "PhoneService": "phone_service",
    "MultipleLines": "multiple_lines",
    "InternetService": "internet_service",
    "OnlineSecurity": "online_security",
    "OnlineBackup": "online_backup",
    "DeviceProtection": "device_protection",
    "TechSupport": "tech_support",
    "StreamingTV": "streaming_tv",
    "StreamingMovies": "streaming_movies",
    "Contract": "contract_type",
    "PaperlessBilling": "paperless_billing",
    "PaymentMethod": "payment_method",
    "MonthlyCharges": "monthly_charges",
    "TotalCharges": "total_charges",
    "Churn": "churn",
}

YES_NO_COLUMNS = ["partner", "dependents", "phone_service", "paperless_billing", "churn"]


def load_and_coerce(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    logger.info("Read %d rows, %d columns from %s", len(df), len(df.columns), csv_path.name)

    df = df.rename(columns=COLUMN_MAP)

    df["senior_citizen"] = df["senior_citizen"].astype(bool)
    for col in YES_NO_COLUMNS:
        df[col] = df[col].map({"Yes": True, "No": False})

    # Blank TotalCharges (zero-tenure customers) becomes NULL, not 0, at load
    # time -- deciding what to do about it is a cleaning decision (FR-2),
    # not an ingestion one.
    df["total_charges"] = pd.to_numeric(df["total_charges"], errors="coerce")

    return df


def load_to_postgres(df: pd.DataFrame) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE customers"))
        df.to_sql("customers", conn, if_exists="append", index=False)
    logger.info("Loaded %d rows into customers", len(df))


def main() -> None:
    if not RAW_CSV_PATH.exists():
        logger.error("Raw CSV not found at %s", RAW_CSV_PATH)
        sys.exit(1)

    try:
        df = load_and_coerce(RAW_CSV_PATH)
        load_to_postgres(df)
    except Exception:
        logger.exception("Load failed")
        sys.exit(1)

    logger.info("Load complete.")


if __name__ == "__main__":
    main()
