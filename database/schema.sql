-- ============================================================================
-- schema.sql
-- Table definition for the IBM Telco Customer Churn dataset.
--
-- Design notes:
-- - Column names are snake_case; the source CSV uses camelCase/PascalCase
--   (e.g. "customerID", "MonthlyCharges") — load_data.py (Phase 2) maps
--   CSV columns to these names on ingestion.
-- - total_charges is nullable: the source data leaves it blank for
--   customers with tenure_months = 0 (brand-new customers who haven't been
--   billed yet). That's handled in preprocessing (Phase 2), not here.
-- - CHECK constraints on categorical columns enumerate the exact values the
--   published dataset uses, so a bad load fails loudly instead of silently
--   inserting a typo'd category.
-- - Re-runnable: DROP TABLE IF EXISTS before CREATE TABLE.
-- ============================================================================

DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id         VARCHAR(20)   PRIMARY KEY,
    gender              VARCHAR(10)   NOT NULL CHECK (gender IN ('Male', 'Female')),
    senior_citizen      BOOLEAN       NOT NULL,
    partner             BOOLEAN       NOT NULL,
    dependents          BOOLEAN       NOT NULL,
    tenure_months       INTEGER       NOT NULL CHECK (tenure_months >= 0),

    phone_service       BOOLEAN       NOT NULL,
    multiple_lines      VARCHAR(20)   CHECK (multiple_lines IN ('Yes', 'No', 'No phone service')),

    internet_service    VARCHAR(20)   CHECK (internet_service IN ('DSL', 'Fiber optic', 'No')),
    online_security     VARCHAR(20)   CHECK (online_security IN ('Yes', 'No', 'No internet service')),
    online_backup       VARCHAR(20)   CHECK (online_backup IN ('Yes', 'No', 'No internet service')),
    device_protection   VARCHAR(20)   CHECK (device_protection IN ('Yes', 'No', 'No internet service')),
    tech_support        VARCHAR(20)   CHECK (tech_support IN ('Yes', 'No', 'No internet service')),
    streaming_tv        VARCHAR(20)   CHECK (streaming_tv IN ('Yes', 'No', 'No internet service')),
    streaming_movies    VARCHAR(20)   CHECK (streaming_movies IN ('Yes', 'No', 'No internet service')),

    contract_type       VARCHAR(20)   NOT NULL CHECK (contract_type IN ('Month-to-month', 'One year', 'Two year')),
    paperless_billing   BOOLEAN       NOT NULL,
    payment_method      VARCHAR(30)   NOT NULL CHECK (payment_method IN (
                            'Electronic check', 'Mailed check',
                            'Bank transfer (automatic)', 'Credit card (automatic)'
                        )),

    monthly_charges     NUMERIC(8,2)  NOT NULL CHECK (monthly_charges >= 0),
    total_charges       NUMERIC(10,2) CHECK (total_charges >= 0),  -- nullable: blank in source for tenure = 0

    churn               BOOLEAN       NOT NULL
);

-- Frequent grouping/filtering column for FR-3 business analytics
-- (contract-type churn breakdowns are one of the first questions asked of this data).
CREATE INDEX idx_customers_contract_type ON customers(contract_type);

-- The target label itself — nearly every analytics/report query filters or
-- groups by churn status, so it's worth the write-time overhead at this scale.
CREATE INDEX idx_customers_churn ON customers(churn);
