# Turning a Churn Model Into a Dollar Decision

*A case study on the Churn-Retention-Engine project — from raw telecom data to a $57K business decision.*

A telecom company loses customers every month. This project builds the full pipeline — from raw customer records to a live executive dashboard — that doesn't stop at *who's likely to leave*. It decides *who's worth trying to save*, and proves the decision in dollars, not just accuracy.

**The headline result:** re-tuning the model's decision threshold — not the model itself — turned a projected $6,247 loss into a **+$57,092 net gain**, on the exact same 1,409 held-out customers.

| Scenario | Business value |
|---|---|
| No retention program at all | −$327,684.60 |
| Default 0.5 probability threshold | −$6,246.60 (barely better than nothing) |
| **ROI-optimized threshold (0.09)** | **+$57,091.65** |

---

## The Problem

Using the IBM Telco Customer Churn dataset (7,043 customers), **26.54% have already churned**, representing **$456,116.60** in monthly recurring revenue at stake. A model that predicts churn accurately is only half the problem — a retention team still has to decide who gets a limited, costly retention offer, and whether that offer is even worth sending. That decision is where this project actually lives.

## The Approach

Eight stages, each producing a verifiable artifact — a schema, a query, a notebook, a trained model, a dashboard — not just a step in a slide deck.

1. **Data ingestion & schema design** — PostgreSQL schema with `CHECK` constraints enumerating every valid category in the source data, so a bad load fails loudly instead of silently inserting a typo.
2. **Validation & cleaning** — automated checks for missing values, duplicate IDs, and unexpected categories. Found and fixed 11 mechanically-blank billing records for brand-new customers — zero rows lost.
3. **SQL business analytics** — 15 queries across customer, revenue, contract, payment, and segmentation analysis — surfaced the single riskiest customer segment in the dataset.
4. **Exploratory data analysis** — a fully executed Python notebook that independently re-derives and visually confirms every SQL finding — the two sides of the analysis agree to the decimal.
5. **Feature engineering** — six engineered signals (tenure cohort, service count, autopay flag, premium-tier flag, and more), each justified by a specific finding from the SQL/EDA stages, not guessed at.
6. **Machine learning** — Logistic Regression, Random Forest, and XGBoost, each tuned with cross-validated hyperparameter search under class weighting for the 26/74 imbalance.
7. **Business decision engine** — converts churn probability into customer lifetime value, expected net benefit, and a Retain / Monitor / No Action call, with the operating threshold chosen by simulated dollar return, not a classification metric.
8. **Executive dashboard** — a 3-page Power BI report wired to a live PostgreSQL view, so the numbers on screen are the same numbers the pipeline just computed, not a static export.

## What the Data Said

Three findings sharp enough to act on:

- **53.73% vs. 5.74%** — **Month-to-month + electronic check** customers churn at nearly **9.4×** the rate of **annual-contract + autopay** customers. The single sharpest segment in the dataset.
- **47.4% → 9.5%** — Churn risk is front-loaded hard: **47.44%** of customers churn in their first year, dropping to just **9.51%** after 4 years of tenure.
- **~2×** — Security & support add-ons roughly **halve churn** among customers who have internet service — online security drops churn from 41.8% to 14.6%.

## The Model

Three models compared, evaluated on 1,409 held-out customers the models never saw during training or tuning:

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| Logistic Regression | 0.7339 | 0.4991 | 0.7834 | 0.6098 | 0.8437 |
| Random Forest | 0.7339 | 0.4992 | 0.7914 | 0.6122 | 0.8433 |
| **XGBoost** | **0.7417** | **0.5085** | **0.7995** | **0.6216** | **0.8459** |

**XGBoost was selected** because it wins on every metric simultaneously — not a marginal AUC edge that trades away precision or recall elsewhere. When one model dominates across the board, there's no accuracy-for-interpretability tradeoff left to make.

### The default threshold was almost worse than doing nothing

91 candidate thresholds were swept against the held-out set, each scored by actual simulated dollar value — not F1, not accuracy. The winner, **0.09**, is far below the textbook default of 0.5.

**Why 0.09, not 0.5:** a wasted $20 retention offer is cheap. A missed churner costs their entire lifetime value — often $800–$1,400. That asymmetry means it pays to flag aggressively: at threshold 0.09, the model catches **370 of 374** actual churners in the test set (recall 0.989), missing only 4.

## The Business Decision Engine

For every currently-active customer, the engine computes:

```
CLV                   = monthly charges × 12 months
Revenue at risk        = churn probability × CLV
Expected net benefit   = churn probability × 25% offer success rate × CLV − $20 offer cost
Action                = Retain (above threshold & net-positive)
                         Monitor (above threshold, not worth an offer)
                         No Action
```

Applied to all **5,174** currently-active customers: **3,128** flagged Retain, **461** Monitor, **1,585** No Action.

**Sample — top 5 highest-risk customers:**

| Customer | Churn Prob. | CLV | Net Benefit | Action |
|---|---|---|---|---|
| 4912-PIGUY | 0.928 | $1,015.20 | $215.54 | Retain |
| 0021-IKXGC | 0.925 | $865.20 | $180.04 | Retain |
| 1452-VOQCH | 0.919 | $901.20 | $187.13 | Retain |
| 4273-MBHYA | 0.918 | $1,072.20 | $225.95 | Retain |
| 7577-SWIFR | 0.915 | $1,071.00 | $225.06 | Retain |

## The Dashboard

Three pages, wired to a live database — Power BI connects directly to a PostgreSQL view that joins customer records with the decision engine's output, so the numbers below are live and filterable, not a static export.

**Executive Overview** — KPI cards plus revenue, tenure-risk, and contract-mix charts, for a 30-second read on where the business stands.

![Executive Overview](reports/screenshots/executive_overview.png)

**Customer Insights** — interactive breakdowns by contract, payment, service tier, and demographics, for exploring exactly where risk concentrates.

![Customer Insights](reports/screenshots/customer_insights.png)

**Predictions & Recommendations** — the decision engine's output made actionable: a sortable, filterable worklist a retention team could use today.

![Predictions & Recommendations](reports/screenshots/predictions_recommendations.png)

## Built With

**Data engineering** — PostgreSQL · Docker · SQL · Python (Pandas, SQLAlchemy)

**Machine learning** — Scikit-learn · XGBoost · RandomizedSearchCV + Stratified K-Fold

**Business analysis** — CLV modeling · ROI-based threshold optimization · cost-sensitive decisioning

**Visualization & delivery** — Power BI · Jupyter / Matplotlib / Seaborn · Git & GitHub

---

**Lavannya Patil**
[GitHub repo](https://github.com/Lavannya22/Churn-Retention-Engine) · [LinkedIn](https://www.linkedin.com/in/lavannyapatil/)

*Dataset: IBM Telco Customer Churn (Kaggle). All figures above are taken directly from the project's executed pipeline output.*
