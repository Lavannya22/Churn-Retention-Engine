-- ============================================================================
-- dashboard_view.sql
-- FR-8: One consolidated view for Power BI to connect to directly (a live
-- Postgres connection, rather than a flat CSV export).
--
-- LEFT JOIN because retention_recommendations only covers currently-active
-- (not yet churned) customers -- see src/retention_strategy.py. Customers
-- who've already churned show NULL for churn_probability/clv/etc., which is
-- correct: there's nothing to recommend for someone who's already gone.
-- ============================================================================

CREATE OR REPLACE VIEW customer_dashboard AS
SELECT
    c.customer_id,
    c.gender,
    c.senior_citizen,
    c.partner,
    c.dependents,
    c.tenure_months,
    c.phone_service,
    c.multiple_lines,
    c.internet_service,
    c.online_security,
    c.online_backup,
    c.device_protection,
    c.tech_support,
    c.streaming_tv,
    c.streaming_movies,
    c.contract_type,
    c.paperless_billing,
    c.payment_method,
    c.monthly_charges,
    c.total_charges,
    c.churn,
    r.churn_probability,
    r.clv,
    r.revenue_at_risk,
    r.retention_offer_cost,
    r.expected_net_benefit,
    r.recommended_action
FROM customers c
LEFT JOIN retention_recommendations r ON c.customer_id = r.customer_id;
