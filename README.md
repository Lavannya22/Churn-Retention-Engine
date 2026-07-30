# Churn-Retention-Engine

**Customer Churn Analytics Platform with Business-Driven Retention Strategy**

> 🚧 Draft README — written before the build starts. Sections marked `TODO` get filled in as each phase completes (see `IMPLEMENTATION_ROADMAP.md`). This isn't meant to be finished until Phase 8.

---

## Overview

A telecom company is losing customers every month. This project builds an end-to-end analytics platform to answer:

- Which customers are likely to churn?
- Why are they leaving?
- How much revenue is at risk?
- Which customers should receive a retention offer — and is that better than targeting people at random?

Rather than stopping at a trained model, this project includes a **Business Decision Engine** that converts churn predictions into a per-customer recommendation (Retain / Monitor / No Action), based on estimated customer lifetime value, retention offer cost, and expected net benefit — with the model's classification threshold chosen to maximize business ROI, not left at a default 0.5.

## Architecture

```text
IBM Telco Dataset
        │
        ▼
PostgreSQL Database
        │
        ▼
Data Validation & Cleaning
        │
        ▼
SQL Business Analytics
        │
        ▼
Exploratory Data Analysis
        │
        ▼
Feature Engineering
        │
        ▼
Machine Learning Models
        │
        ▼
Business Decision Engine
        │
        ▼
Power BI Dashboard
```

## Tech Stack

| Layer | Technology |
|---|---|
| Database | PostgreSQL |
| Query Language | SQL |
| Programming | Python (Pandas, NumPy) |
| Machine Learning | Scikit-learn, XGBoost |
| Visualization | Power BI |
| Version Control | Git & GitHub |

## Dataset

[IBM Telco Customer Churn Dataset](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) — ~7,043 customers, 21 features, binary churn label.

## Repository Structure

```text
Churn-Retention-Engine/
│
├── data/
│   ├── raw/                      # Original CSV
│   └── processed/                # Cleaned dataset
│
├── database/
│   ├── schema.sql
│   └── analysis_queries.sql
│
├── notebooks/
│   └── EDA.ipynb
│
├── src/
│   ├── load_data.py
│   ├── validation.py
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── train_model.py
│   ├── evaluate_model.py
│   └── retention_strategy.py
│
├── models/
├── dashboard/
│   └── Customer_Churn.pbix
├── reports/
│   └── screenshots/
│
├── README.md
├── requirements.txt
└── .gitignore
```

## Setup

```bash
# Clone the repo
git clone https://github.com/Lavannya22/Churn-Retention-Engine.git
cd Churn-Retention-Engine

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure your local database connection
cp .env.example .env        # then fill in your PostgreSQL credentials

# Set up the database
psql -U <user> -d <database> -f database/schema.sql

# Run the pipeline
python src/load_data.py
python src/validation.py
python src/preprocessing.py
python src/feature_engineering.py
python src/train_model.py
python src/evaluate_model.py
python src/retention_strategy.py
```

`TODO`: confirm this list matches the final script names/order once Phase 2–6 are built.

## Key Business Insights

`TODO` — fill in with the 2–3 sharpest, most specific findings from Phase 3 (SQL analytics) and Phase 4 (EDA). Not generic ("month-to-month churns more") — specific and quantified (e.g., "customers on month-to-month contracts paying by electronic check churn at X%, compared to Y% for autopay customers on annual contracts").

## Model Performance

`TODO` — fill in after Phase 5/6:
- Models compared and final selection rationale
- Key metrics (ROC-AUC, Precision, Recall, F1) at the chosen operating threshold
- Why that threshold was chosen over the default 0.5

## Business Decision Engine

`TODO` — fill in after Phase 6:
- CLV formula used and why
- Retention offer cost and success rate assumptions
- How recommendations (Retain / Monitor / No Action) are generated
- Example: a sample of high-risk customers and their recommended actions

## Dashboard

`TODO` — add screenshots from `reports/screenshots/` for all three pages (Executive Overview, Customer Insights, Predictions & Recommendations) once Phase 7 is done.

## Assumptions & Limitations

- Retention offer cost: $20/customer
- Retention offer success rate: 25%
- CLV approximated as `Monthly Charges × Expected Remaining Months` — a simplification that doesn't account for discounting or churn-adjusted expected tenure
- Dataset is a single snapshot, not a time series — no seasonality or trend effects are modeled
- `TODO`: add any additional limitations discovered during the build

## Future Improvements

- SHAP-based model explainability (per-customer "why" behind each prediction)
- Retention campaign ROI simulation vs. random targeting
- Dashboard what-if analysis / dynamic ROI scenarios

## Author

`TODO`
