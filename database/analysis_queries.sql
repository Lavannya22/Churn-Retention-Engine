-- ============================================================================
-- analysis_queries.sql
-- FR-3: Business SQL analytics against the cleaned `customers` table.
-- Organized by business category; each query is preceded by a one-line
-- comment stating the question it answers.
-- ============================================================================


-- ============================================================
-- 1. Customer Metrics
-- ============================================================

-- How many customers do we have, and what fraction have churned?
SELECT
    count(*)                                        AS total_customers,
    sum(CASE WHEN churn THEN 1 ELSE 0 END)           AS churned_customers,
    round(100.0 * sum(CASE WHEN churn THEN 1 ELSE 0 END) / count(*), 2) AS churn_rate_pct
FROM customers;

-- Does churn skew by gender, senior citizen status, partner, or dependents?
SELECT
    'gender' AS dimension, gender AS value,
    count(*) AS customers,
    round(100.0 * sum(CASE WHEN churn THEN 1 ELSE 0 END) / count(*), 2) AS churn_rate_pct
FROM customers GROUP BY gender
UNION ALL
SELECT
    'senior_citizen', senior_citizen::text,
    count(*),
    round(100.0 * sum(CASE WHEN churn THEN 1 ELSE 0 END) / count(*), 2)
FROM customers GROUP BY senior_citizen
UNION ALL
SELECT
    'partner', partner::text,
    count(*),
    round(100.0 * sum(CASE WHEN churn THEN 1 ELSE 0 END) / count(*), 2)
FROM customers GROUP BY partner
UNION ALL
SELECT
    'dependents', dependents::text,
    count(*),
    round(100.0 * sum(CASE WHEN churn THEN 1 ELSE 0 END) / count(*), 2)
FROM customers GROUP BY dependents
ORDER BY dimension, value;

-- How does average tenure differ between churned and retained customers?
SELECT
    churn,
    count(*)                          AS customers,
    round(avg(tenure_months), 1)      AS avg_tenure_months
FROM customers
GROUP BY churn
ORDER BY churn;


-- ============================================================
-- 2. Revenue Metrics
-- ============================================================

-- What's our total and average monthly recurring revenue?
SELECT
    round(sum(monthly_charges), 2)  AS total_monthly_revenue,
    round(avg(monthly_charges), 2)  AS avg_monthly_charges
FROM customers;

-- How much monthly revenue is currently attached to customers who've already churned
-- (a proxy for revenue that walked out the door)?
SELECT
    round(sum(CASE WHEN churn THEN monthly_charges ELSE 0 END), 2) AS churned_monthly_revenue,
    round(sum(CASE WHEN NOT churn THEN monthly_charges ELSE 0 END), 2) AS retained_monthly_revenue,
    round(100.0 * sum(CASE WHEN churn THEN monthly_charges ELSE 0 END)
        / sum(monthly_charges), 2) AS pct_revenue_from_churned
FROM customers;

-- How is monthly revenue distributed across contract types?
SELECT
    contract_type,
    count(*)                        AS customers,
    round(sum(monthly_charges), 2)  AS total_monthly_revenue,
    round(avg(monthly_charges), 2)  AS avg_monthly_charges
FROM customers
GROUP BY contract_type
ORDER BY total_monthly_revenue DESC;


-- ============================================================
-- 3. Contract Analysis
-- ============================================================

-- Which contract type churns the most, and by how much relative to the others?
SELECT
    contract_type,
    count(*) AS customers,
    sum(CASE WHEN churn THEN 1 ELSE 0 END) AS churned,
    round(100.0 * sum(CASE WHEN churn THEN 1 ELSE 0 END) / count(*), 2) AS churn_rate_pct
FROM customers
GROUP BY contract_type
ORDER BY churn_rate_pct DESC;

-- Do longer-committed customers also stay longer in practice (avg tenure by contract)?
SELECT
    contract_type,
    round(avg(tenure_months), 1) AS avg_tenure_months
FROM customers
GROUP BY contract_type
ORDER BY avg_tenure_months DESC;


-- ============================================================
-- 4. Payment Analysis
-- ============================================================

-- Which payment method is associated with the highest churn?
SELECT
    payment_method,
    count(*) AS customers,
    sum(CASE WHEN churn THEN 1 ELSE 0 END) AS churned,
    round(100.0 * sum(CASE WHEN churn THEN 1 ELSE 0 END) / count(*), 2) AS churn_rate_pct
FROM customers
GROUP BY payment_method
ORDER BY churn_rate_pct DESC;

-- Does paperless billing correlate with churn?
SELECT
    paperless_billing,
    count(*) AS customers,
    round(100.0 * sum(CASE WHEN churn THEN 1 ELSE 0 END) / count(*), 2) AS churn_rate_pct
FROM customers
GROUP BY paperless_billing;

-- The standout risk segment: month-to-month contract + electronic check payment,
-- compared against the most stable segment (long contract + autopay).
SELECT
    CASE
        WHEN contract_type = 'Month-to-month' AND payment_method = 'Electronic check'
            THEN 'Month-to-month + Electronic check'
        WHEN contract_type IN ('One year', 'Two year')
             AND payment_method IN ('Bank transfer (automatic)', 'Credit card (automatic)')
            THEN 'Annual+ contract + Autopay'
        ELSE 'Other'
    END AS segment,
    count(*) AS customers,
    round(100.0 * sum(CASE WHEN churn THEN 1 ELSE 0 END) / count(*), 2) AS churn_rate_pct
FROM customers
GROUP BY segment
ORDER BY churn_rate_pct DESC;


-- ============================================================
-- 5. Internet Service Analysis
-- ============================================================

-- Which internet service type churns the most?
SELECT
    internet_service,
    count(*) AS customers,
    round(100.0 * sum(CASE WHEN churn THEN 1 ELSE 0 END) / count(*), 2) AS churn_rate_pct,
    round(avg(monthly_charges), 2) AS avg_monthly_charges
FROM customers
GROUP BY internet_service
ORDER BY churn_rate_pct DESC;

-- Do add-on services (security/backup/protection/support) reduce churn for
-- fiber/DSL customers who have internet service at all?
SELECT
    'online_security' AS add_on, online_security AS status,
    count(*) AS customers,
    round(100.0 * sum(CASE WHEN churn THEN 1 ELSE 0 END) / count(*), 2) AS churn_rate_pct
FROM customers WHERE internet_service != 'No' GROUP BY online_security
UNION ALL
SELECT
    'tech_support', tech_support,
    count(*),
    round(100.0 * sum(CASE WHEN churn THEN 1 ELSE 0 END) / count(*), 2)
FROM customers WHERE internet_service != 'No' GROUP BY tech_support
UNION ALL
SELECT
    'online_backup', online_backup,
    count(*),
    round(100.0 * sum(CASE WHEN churn THEN 1 ELSE 0 END) / count(*), 2)
FROM customers WHERE internet_service != 'No' GROUP BY online_backup
UNION ALL
SELECT
    'device_protection', device_protection,
    count(*),
    round(100.0 * sum(CASE WHEN churn THEN 1 ELSE 0 END) / count(*), 2)
FROM customers WHERE internet_service != 'No' GROUP BY device_protection
ORDER BY add_on, status;


-- ============================================================
-- 6. Customer Segmentation
-- ============================================================

-- How does churn vary across tenure buckets (new vs. established customers)?
SELECT
    CASE
        WHEN tenure_months <= 12 THEN '0-12 months'
        WHEN tenure_months <= 24 THEN '13-24 months'
        WHEN tenure_months <= 48 THEN '25-48 months'
        ELSE '49+ months'
    END AS tenure_bucket,
    count(*) AS customers,
    round(100.0 * sum(CASE WHEN churn THEN 1 ELSE 0 END) / count(*), 2) AS churn_rate_pct
FROM customers
GROUP BY tenure_bucket
ORDER BY min(tenure_months);

-- Are high-spending customers (top quartile monthly charges) more or less likely to churn?
WITH quartile AS (
    SELECT customer_id, monthly_charges, churn,
           ntile(4) OVER (ORDER BY monthly_charges) AS spend_quartile
    FROM customers
)
SELECT
    spend_quartile,
    count(*) AS customers,
    round(min(monthly_charges), 2) AS min_monthly_charges,
    round(max(monthly_charges), 2) AS max_monthly_charges,
    round(100.0 * sum(CASE WHEN churn THEN 1 ELSE 0 END) / count(*), 2) AS churn_rate_pct
FROM quartile
GROUP BY spend_quartile
ORDER BY spend_quartile;

-- Full segmentation matrix: contract type x payment method churn rate,
-- to spot the single riskiest combination (used for the README's headline finding).
SELECT
    contract_type,
    payment_method,
    count(*) AS customers,
    round(100.0 * sum(CASE WHEN churn THEN 1 ELSE 0 END) / count(*), 2) AS churn_rate_pct
FROM customers
GROUP BY contract_type, payment_method
HAVING count(*) >= 20  -- drop tiny cells that would make the rate noisy
ORDER BY churn_rate_pct DESC;
