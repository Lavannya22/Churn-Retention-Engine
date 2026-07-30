# Phase 3 — SQL Analytics: Actual Output Numbers

Scratch notes captured from running `database/analysis_queries.sql` against
the cleaned `customers` table (7,043 rows). Not polished writing -- just the
real numbers so Phase 4/8 don't require re-running everything.

## Headline finding

**Month-to-month + Electronic check** customers churn at **53.73%**
(n=1,850), vs. **5.74%** for **Annual-contract (1yr/2yr) + Autopay**
customers (n=1,934) -- a ~9.4x difference. This is the sharpest, most
specific finding for the README.

## 1. Customer Metrics
- Total customers: 7,043. Churned: 1,869 (26.54%).
- Churn by dependents: no dependents 31.28% vs. has dependents 15.45%.
- Churn by partner: no partner 32.96% vs. has partner 19.66%.
- Churn by senior citizen: non-senior 23.61% vs. senior 41.68%.
- Churn by gender: essentially flat (Female 26.92%, Male 26.16%) -- not a
  meaningful driver.
- Avg tenure: retained customers 37.6 months vs. churned 18.0 months.

## 2. Revenue Metrics
- Total monthly revenue: $456,116.60. Avg monthly charges: $64.76.
- Revenue currently attached to already-churned customers: $139,130.85
  (30.50% of total monthly revenue).
- Revenue by contract: Month-to-month $257,294.15 (3,875 customers),
  Two year $103,005.85 (1,695), One year $95,816.60 (1,473).

## 3. Contract Analysis
- Churn rate: Month-to-month 42.71%, One year 11.27%, Two year 2.83%.
- Avg tenure: Two year 56.7mo, One year 42.0mo, Month-to-month 18.0mo.

## 4. Payment Analysis
- Churn by payment method: Electronic check 45.29% (highest), Mailed check
  19.11%, Bank transfer 16.71%, Credit card 15.24% (lowest).
- Paperless billing customers churn more: 33.57% vs. 16.33% for non-paperless.
- See headline finding above for the combined segment.

## 5. Internet Service Analysis
- Churn by internet service: Fiber optic 41.89% (avg $91.50/mo), DSL 18.96%
  (avg $58.10/mo), No internet 7.40% (avg $21.08/mo).
- Add-ons cut churn roughly in half when present, for customers who have
  internet service at all:
  - online_security: No 41.77% vs. Yes 14.61%
  - tech_support: No 41.64% vs. Yes 15.17%
  - online_backup: No 39.93% vs. Yes 21.53%
  - device_protection: No 39.13% vs. Yes 22.50%

## 6. Customer Segmentation
- Tenure buckets: 0-12mo 47.44% churn, 13-24mo 28.71%, 25-48mo 20.39%,
  49+mo 9.51%. Churn risk drops steadily and substantially with tenure.
- Monthly-charge quartiles: Q1 (\$18.25-35.50) 11.24% churn, Q2 24.65%,
  Q3 (\$70.35-89.85) 37.42% (highest), Q4 (top spenders) 32.84% -- churn
  peaks in Q3, not at the very top, worth a sentence in the EDA writeup.
- Full contract x payment matrix (12 cells, all n>=20) ranges from 53.73%
  (Month-to-month/Electronic check) down to 0.79% (Two year/Mailed check).
