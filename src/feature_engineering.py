"""FR-5: Engineer features on top of the cleaned dataset.

Run after preprocessing.py. Reads data/processed/customers_clean.csv and
writes data/processed/customers_features.csv, ready for Phase 5 modeling.

Every feature here is derivable from information available about a customer
*before* they churn (tenure, pricing, services subscribed, payment method) --
none of them use churn or any post-outcome information, so there's no
leakage risk.
"""

import logging
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "customers_clean.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "customers_features.csv"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Matches the tenure buckets already used in Phase 3's SQL segmentation query
# (database/analysis_queries.sql, Section 6), so the same "0-12 months churns
# ~47%" story holds whether you're reading the SQL output or the model input.
TENURE_BINS = [-1, 12, 24, 48, 1000]
TENURE_LABELS = ["0-12 months", "13-24 months", "25-48 months", "49+ months"]

SERVICE_ADDON_COLUMNS = [
    "multiple_lines",
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_tv",
    "streaming_movies",
]

AUTOPAY_METHODS = {"Bank transfer (automatic)", "Credit card (automatic)"}


def add_tenure_group(df: pd.DataFrame) -> pd.DataFrame:
    """Bucket tenure into the same 4 groups used in Phase 3's SQL segmentation.

    Churn risk isn't linear in tenure (it drops off steeply after year 1, per
    Phase 3/4 findings) -- a categorical bucket lets tree-based models split on
    that non-linearity directly instead of hunting for it in a raw integer.
    """
    df["tenure_group"] = pd.cut(df["tenure_months"], bins=TENURE_BINS, labels=TENURE_LABELS)
    return df


def add_service_count(df: pd.DataFrame) -> pd.DataFrame:
    """Count how many services a customer subscribes to (0-9).

    Counts phone_service, having internet at all, and each of the 7 add-ons
    (multiple_lines / online_security / online_backup / device_protection /
    tech_support / streaming_tv / streaming_movies) when set to 'Yes'.
    Business reasoning: a customer bundled into more services has more
    switching friction and more to lose by leaving -- higher service count is
    a reasonable proxy for engagement/stickiness.
    """
    has_internet = (df["internet_service"] != "No").astype(int)
    addon_yes_count = (df[SERVICE_ADDON_COLUMNS] == "Yes").sum(axis=1)
    df["service_count"] = df["phone_service"].astype(int) + has_internet + addon_yes_count
    return df


def add_high_value_customer(df: pd.DataFrame) -> pd.DataFrame:
    """Flag customers with above-median total_charges (revenue billed to date).

    The median is computed from the data itself rather than a hardcoded
    dollar figure, so this stays meaningful if the customer base's pricing
    shifts. This is the customer-value signal that Phase 6's Business
    Decision Engine will weigh against churn probability when deciding who's
    worth a retention offer.
    """
    threshold = df["total_charges"].median()
    df["high_value_customer"] = df["total_charges"] > threshold
    return df


def add_premium_customer(df: pd.DataFrame) -> pd.DataFrame:
    """Flag Fiber optic subscribers as the premium internet tier.

    Fiber optic is priced highest (avg $91.50/mo vs. $58.10 for DSL, per
    Phase 3) and is also the highest-churn internet segment (41.89% vs.
    18.96%) -- a flag worth isolating on its own rather than leaving buried
    inside the 3-way internet_service category.
    """
    df["premium_customer"] = df["internet_service"] == "Fiber optic"
    return df


def add_autopay_customer(df: pd.DataFrame) -> pd.DataFrame:
    """Flag customers on an automatic payment method (bank transfer or credit card).

    Directly reflects Phase 3's finding that autopay customers churn at
    roughly a third the rate of electronic check payers (15-17% vs. 45.29%).
    """
    df["autopay_customer"] = df["payment_method"].isin(AUTOPAY_METHODS)
    return df


def add_revenue_category(df: pd.DataFrame) -> pd.DataFrame:
    """Bucket monthly_charges into Low/Medium/High terciles.

    Computed from the data's own tercile boundaries rather than fixed
    dollar cutoffs. Phase 3's quartile analysis showed churn risk isn't
    monotonic in price (it peaks in the 3rd quartile, not the top) -- a
    categorical bucket lets the model represent that non-linear
    relationship directly.
    """
    df["revenue_category"] = pd.qcut(df["monthly_charges"], q=3, labels=["Low", "Medium", "High"])
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = add_tenure_group(df)
    df = add_service_count(df)
    df = add_high_value_customer(df)
    df = add_premium_customer(df)
    df = add_autopay_customer(df)
    df = add_revenue_category(df)
    return df


def main() -> None:
    df = pd.read_csv(INPUT_PATH)
    logger.info("Loaded %d rows from %s", len(df), INPUT_PATH.name)

    df = engineer_features(df)
    logger.info("Engineered features: tenure_group, service_count, high_value_customer, "
                "premium_customer, autopay_customer, revenue_category")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    logger.info("Wrote %d rows with engineered features to %s", len(df), OUTPUT_PATH)


if __name__ == "__main__":
    main()
