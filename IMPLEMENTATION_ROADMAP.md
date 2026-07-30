# Customer Churn Analytics Platform — Implementation Roadmap

> **Companion document to:** Final Requirements Specification (v1.0 — Frozen)
> **Purpose:** Single source of truth for building the project. Defines directory structure, database schema, task breakdown per FR, Git commit strategy, milestone outputs, dependencies, and Definition of Done for each phase.
> **Rule:** No new requirements get added here. If something's missing, it goes back to the frozen spec for a conscious decision — not silently into the roadmap.

---

## Project Description

A telecom company is losing customers every month and wants to know: **which customers are likely to churn, why, how much revenue is at risk, and who should get a retention offer.**

This project builds an end-to-end analytics platform that answers those questions — from raw data to an executive dashboard — using PostgreSQL, Python, machine learning, and Power BI. It goes beyond a typical churn-prediction notebook by including a **Business Decision Engine**: model predictions are converted into a customer lifetime value estimate, a retention offer cost-benefit calculation, and a concrete recommended action (Retain / Monitor / No Action) per customer — with the model's classification threshold chosen to maximize business ROI rather than left at a default 0.5.

**Core pipeline:** Data Ingestion → Data Validation & Cleaning → SQL Business Analytics → Exploratory Data Analysis → Feature Engineering → Machine Learning → Business Decision Engine → Executive Power BI Dashboard.

Full requirements, assumptions, and scope decisions live in the frozen Requirements Specification (v1.0); this document is the execution plan built on top of it.

---

## How to use this document

Work top to bottom, phase by phase. Each phase lists:
- **Tasks** — what to actually do
- **Depends on** — what must be finished first, and why
- **Deliverables** — files you should have at the end
- **Suggested commits** — Conventional Commit messages, roughly one per meaningful unit of work
- **Definition of Done** — the bar for moving to the next phase
- **Pitfalls** — mistakes that are easy to make at this exact step

Estimated timeline assumes evenings/weekends, roughly 6–10 hours/week. Adjust to your pace — the phase order matters more than the calendar.

---

## Phase 0 — Project Planning
**Estimated time:** 1 day

### Tasks
- Create the GitHub repository (private is fine until it's polished, then flip to public).
- Set up the local folder structure (full tree in Section: Directory Structure below).
- Initialize a Python virtual environment (`venv` or `conda`) and commit `requirements.txt` (empty for now, filled in as you go).
- Write a skeleton `README.md` with just the project title, one-paragraph goal, and a "🚧 Work in Progress" note — you'll flesh it out in Phase 8.
- Add a `.gitignore` (Python + data + Power BI + OS noise — see template below).
- Confirm PostgreSQL is installed locally and you can connect (`psql` or a GUI client like pgAdmin/DBeaver).

### Depends on
Nothing — this is the starting point.

### Deliverables
- Empty-but-structured GitHub repo
- `README.md` (skeleton)
- `.gitignore`
- `requirements.txt` (skeleton)
- Working local PostgreSQL connection

### Suggested commits
```
chore: initialize repository structure
chore: add .gitignore
docs: add skeleton README
```

### Definition of Done
You can run `psql` (or equivalent) and connect to a local database, and your repo has the folder skeleton with no code yet.

### Pitfalls
- Don't skip the virtual environment — "it works on my machine" undermines the reproducibility story you're trying to tell.
- Don't write a long README now. You don't know your own findings yet; a long README written before the work is done tends to get stale and rewritten anyway.

---

## Directory Structure

```text
Churn-Retention-Engine/
│
├── data/
│   ├── raw/                      # Original, untouched CSV (never edited)
│   └── processed/                # Cleaned output from preprocessing.py
│
├── database/
│   ├── schema.sql                # Table definitions, constraints, indexes
│   └── analysis_queries.sql      # FR-3 business SQL, organized by section
│
├── notebooks/
│   └── EDA.ipynb                 # FR-4 — exploration + business interpretation
│
├── src/
│   ├── load_data.py              # FR-1 — CSV → PostgreSQL
│   ├── validation.py             # FR-2 — data quality checks
│   ├── preprocessing.py          # FR-2 — cleaning logic
│   ├── feature_engineering.py    # FR-5 — engineered features
│   ├── train_model.py            # FR-6 — model training
│   ├── evaluate_model.py         # FR-6 — metrics, comparison
│   └── retention_strategy.py     # FR-7 — CLV, threshold, recommendations
│
├── models/
│   └── (saved .pkl files go here — gitignored except a small README noting what's expected)
│
├── dashboard/
│   └── Customer_Churn.pbix       # FR-8
│
├── reports/
│   └── screenshots/              # Dashboard screenshots for the README
│
├── README.md
├── requirements.txt
└── .gitignore
```

**Why this shape:** `data/raw` vs `data/processed` keeps the ETL boundary visible — anyone browsing the repo can tell what's original vs derived. `src/` files map 1:1 to functional requirements, so the code structure mirrors the spec structure, which makes both easier to defend in an interview ("this file is FR-2, here's why it's separate from FR-1").

### .gitignore essentials
```
# Python
venv/
__pycache__/
*.pyc
.ipynb_checkpoints/

# Data (raw CSV can be small enough to commit — your call; processed always regenerable, so ignore)
data/processed/*
!data/processed/.gitkeep

# Models
models/*.pkl

# OS
.DS_Store
Thumbs.db

# Power BI (only ignore .pbix if it's large; usually fine to commit for portfolio visibility)
```
Note: for a portfolio repo, consider **committing** the raw CSV (it's public/small — ~1MB) and the final `.pbix` so a visitor can actually see your work without extra setup steps. Gitignore is more about not committing regenerable intermediate junk.

---

## Phase 1 — Database Design
**Estimated time:** 1–2 days

### Tasks
- Design the `customers` table based on the Telco dataset's 21 columns.
- Choose appropriate PostgreSQL data types (don't default everything to `TEXT`).
- Add constraints: `PRIMARY KEY` on `customer_id`, `CHECK` constraints on categorical fields where sensible (e.g., `gender IN ('Male','Female')`), `NOT NULL` where the business logic requires it.
- Add 1–2 indexes with a stated rationale (e.g., on `contract_type` if you expect to filter/group by it often in FR-3) — not because scale demands it at 7K rows, but to show you know when indexing matters.
- Write `schema.sql` as a standalone, re-runnable script (`DROP TABLE IF EXISTS` + `CREATE TABLE`).

### Depends on
Phase 0 (repo + local Postgres connection). Also implicitly informed by what FR-3's SQL analytics and FR-5's feature engineering will need to query — skim those sections of the frozen spec before finalizing column types.

### Deliverables
- `database/schema.sql`

### Suggested schema sketch
```sql
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id         VARCHAR(20) PRIMARY KEY,
    gender               VARCHAR(10)  NOT NULL CHECK (gender IN ('Male','Female')),
    senior_citizen       BOOLEAN      NOT NULL,
    partner              BOOLEAN      NOT NULL,
    dependents            BOOLEAN      NOT NULL,
    tenure_months         INTEGER      NOT NULL CHECK (tenure_months >= 0),
    phone_service         BOOLEAN      NOT NULL,
    multiple_lines        VARCHAR(30),
    internet_service      VARCHAR(20),
    online_security       VARCHAR(30),
    online_backup         VARCHAR(30),
    device_protection     VARCHAR(30),
    tech_support          VARCHAR(30),
    streaming_tv          VARCHAR(30),
    streaming_movies      VARCHAR(30),
    contract_type         VARCHAR(20)  NOT NULL,
    paperless_billing      BOOLEAN      NOT NULL,
    payment_method         VARCHAR(30)  NOT NULL,
    monthly_charges         NUMERIC(8,2) NOT NULL CHECK (monthly_charges >= 0),
    total_charges           NUMERIC(10,2),           -- nullable: source data has blanks for new customers
    churn                    BOOLEAN      NOT NULL
);

CREATE INDEX idx_customers_contract_type ON customers(contract_type);
CREATE INDEX idx_customers_churn ON customers(churn);
```
Adjust field names/types to match your actual cleaned column names once you've looked at the raw CSV — this is a starting sketch, not gospel.

### Suggested commits
```
feat: add PostgreSQL schema for customers table
feat: add indexes on contract_type and churn
docs: document schema design rationale in schema.sql comments
```

### Definition of Done
Running `schema.sql` against a fresh database creates the table with no errors, and you can `INSERT` a hand-written test row that respects all constraints.

### Pitfalls
- Don't type `total_charges` as `NOT NULL` — the raw dataset has blank values for customers with zero tenure, and you'll handle that in FR-2, not by forcing it here.
- Don't over-index. Two purposeful indexes with a one-line comment each beats five indexes "just in case."

---

## Phase 2 — ETL (FR-1, FR-2)
**Estimated time:** 3–4 days

### Tasks — FR-1 (Data Ingestion)
- Write `load_data.py`: reads the raw CSV, connects to PostgreSQL (via `psycopg2` or `SQLAlchemy`), loads rows into `customers`.
- Add basic logging (Python's `logging` module is enough — timestamps, row counts, success/failure).
- Handle the connection string via an environment variable (`.env` + `python-dotenv`), never hardcoded.

### Tasks — FR-2 (Validation & Cleaning)
- Write `validation.py`: checks for missing values, duplicate `customer_id`s, blank `TotalCharges`, unexpected categorical values, wrong dtypes. Output a short markdown or console summary.
- Write `preprocessing.py`: applies the actual fixes — convert `TotalCharges` blanks (these are all `tenure == 0` customers; decide and document whether you set them to `0` or drop them), cast types, standardize string casing/whitespace in categorical columns, drop duplicates.
- Output the cleaned dataset to `data/processed/`.

### Depends on
Phase 1 (schema must exist to load into). FR-2's cleaning decisions should be made *before* Phase 4 (EDA) since EDA should run on clean data, not raw.

### Deliverables
- `src/load_data.py`
- `src/validation.py`
- `src/preprocessing.py`
- `data/processed/customers_clean.csv` (or loaded directly into a `customers_clean` table/view — your call)

### Suggested commits
```
feat: add environment-based database connection config
feat: implement CSV to PostgreSQL ingestion (FR-1)
feat: add data validation checks (FR-2)
fix: handle blank TotalCharges for zero-tenure customers
feat: implement data cleaning pipeline (FR-2)
docs: document cleaning decisions and rationale
```

### Definition of Done
Running `load_data.py` then `validation.py` then `preprocessing.py` end-to-end, on a fresh clone of the repo (with `.env` set up per your README instructions), produces a clean dataset with zero missing values in required fields and no duplicate customer IDs.

### Pitfalls
- **This is the #1 place data leakage sneaks in later** if you're not careful: if you compute anything here based on the full dataset's statistics (e.g., filling missing values with a global mean), remember whether that same logic needs to be train/test-aware once you get to Phase 5. For this dataset, missing values are mechanical (`TotalCharges` blank because `tenure=0`), not statistical, so it's less of a risk here — but note it now so it's not a surprise later.
- Log *what* you cleaned and *why*, not just "cleaning complete" — this log becomes README material later.

---

## Phase 3 — SQL Analytics (FR-3)
**Estimated time:** 2–3 days

### Tasks
- Write `analysis_queries.sql`, organized into clearly commented sections matching the frozen spec's categories: Customer Metrics, Revenue Metrics, Contract Analysis, Payment Analysis, Internet Service Analysis, Customer Segmentation.
- For each query, add a one-line comment above it stating the business question it answers.
- Optionally, create 1–2 SQL views for queries you'll reuse later (e.g., a `customer_summary` view) — noted as optional in the frozen spec, don't force it if it doesn't add clarity.
- Run each query against your cleaned data and **save the actual output** (screenshot or markdown table) — you'll want these numbers for the README's business insights section later, and for sanity-checking your EDA in Phase 4.

### Depends on
Phase 2 (needs clean data loaded).

### Deliverables
- `database/analysis_queries.sql`
- A scratch notes file (not necessarily committed) with the actual output numbers, so you don't have to re-run everything when writing the README

### Suggested commits
```
feat: add SQL queries for customer and revenue metrics
feat: add SQL queries for contract and payment analysis
feat: add SQL queries for customer segmentation
docs: annotate each query with its business question
```

### Definition of Done
Every query in the file runs without error against the cleaned table and returns a sensible result you could explain out loud (e.g., "month-to-month contracts churn at X%, more than double annual contracts").

### Pitfalls
- Don't just write queries and move on — actually read the numbers. This phase is where you should start noticing the specific finding that'll become your standout README insight (per the very first review in this thread: recruiters have seen generic Telco dashboards; your specific finding is what differentiates yours).

---

## Phase 4 — Python Analytics: EDA + Feature Engineering (FR-4, FR-5)
**Estimated time:** 4–5 days

### Tasks — FR-4 (EDA)
- Build `EDA.ipynb` covering: churn distribution, monthly charges distribution, tenure distribution, correlation heatmap, contract/payment/internet service breakdowns, boxplots for numerical features vs churn.
- Under every chart, write 2–3 sentences: what it shows, why it matters to the business, and (where relevant) how it connects to a query result from Phase 3.

### Tasks — FR-5 (Feature Engineering)
- Write `feature_engineering.py` implementing: Tenure Group, Service Count, High Value Customer, Premium Customer, AutoPay Customer, Revenue Category.
- For each feature, add a docstring or comment explaining the business reasoning (not just the code) — this is explicitly required by the frozen spec and is easy to skip under time pressure.
- Output the feature-engineered dataset ready for modeling.

### Depends on
Phase 2 (clean data). Feature engineering should be finalized before Phase 5 so your train/test split happens on the final feature set, not a partial one.

### Deliverables
- `notebooks/EDA.ipynb`
- `src/feature_engineering.py`

### Suggested commits
```
feat: add EDA notebook - distributions and churn breakdown
feat: add EDA notebook - correlation and boxplot analysis
docs: add business interpretation to EDA visualizations
feat: implement tenure group and service count features
feat: implement customer value and payment behavior features
docs: document feature engineering rationale
```

### Definition of Done
The EDA notebook runs top-to-bottom without errors and every chart has a written interpretation. `feature_engineering.py` takes the cleaned dataset and returns a dataframe with all new features, each documented.

### Pitfalls
- **Leakage risk lives here.** If any engineered feature is derived using information that wouldn't be available at prediction time (e.g., something correlated with the outcome that's really just churn in disguise), it'll quietly inflate your model's metrics in Phase 5. Sanity-check each feature: "would I know this about a customer *before* they churn?"
- Don't let the EDA notebook become 40 unlabeled charts. Fewer charts with real interpretation beats more charts with none.

---

## Phase 5 — Machine Learning (FR-6)
**Estimated time:** 5–7 days

### Tasks
- Write `train_model.py`: stratified train/test split, train Logistic Regression (baseline), Random Forest, XGBoost. Apply class weights to handle the ~26/74 imbalance. Optionally compare against SMOTE, but don't let this become a rabbit hole — one clean comparison is enough.
- Use stratified k-fold cross-validation and basic hyperparameter tuning (`GridSearchCV` or `RandomizedSearchCV` — randomized is faster and usually sufficient at this data size).
- Write `evaluate_model.py`: compute Accuracy, Precision, Recall, F1, ROC-AUC, and a Confusion Matrix for each model, at the **default 0.5 threshold** (per the frozen spec's explicit note — final threshold is chosen in Phase 6, not here).
- Compare the three models and write a short justification for your final pick — this doesn't have to be the highest-AUC model if, e.g., a slightly-lower-AUC model is meaningfully more interpretable and that tradeoff matters to you; just state your reasoning.

### Depends on
Phase 4 (final feature set). This phase's evaluation is intentionally incomplete until Phase 6 sets the operating threshold — see the note below.

### Deliverables
- `src/train_model.py`
- `src/evaluate_model.py`
- `models/` — saved model file(s) (gitignored, but document in a small `models/README.md` what should be there and how to regenerate it)
- A short `model_comparison` writeup (can live in the main README or a separate `reports/model_comparison.md` — your call, given the earlier discussion about not over-multiplying report files)

### Suggested commits
```
feat: implement stratified train/test split
feat: train baseline logistic regression model
feat: train random forest and xgboost models
feat: add cross-validation and hyperparameter tuning
feat: implement model evaluation metrics
docs: add model comparison and final selection rationale
```

### Definition of Done
All three models train and evaluate without error. You have a clear, written answer to "why did you choose your final model" that references actual numbers, not just "XGBoost is usually best."

### ⚠️ Important dependency note (carried over from the frozen spec)
FR-6's evaluation here is **threshold-independent by design** — ROC-AUC and the default-threshold metrics tell you about model *quality*, not the *operating point* you'll actually use. Don't treat the 0.5-threshold confusion matrix as final. Phase 6 will select the real threshold based on business ROI, and you'll come back and add a short addendum to this phase's evaluation once that's chosen. This isn't rework — it's the plan.

### Pitfalls
- Don't over-tune. Diminishing returns hit fast on a 7K-row dataset; a few hours of `RandomizedSearchCV` is plenty. Time spent squeezing 0.83 to 0.84 AUC is time not spent on the business layer, which is your actual differentiator.
- Make sure the train/test split happens *after* all feature engineering that could leak, and that any scaling/encoding fit (e.g., `StandardScaler`, target encoding) is fit on train only and applied to test — a classic, easy-to-miss leakage source.

---

## Phase 6 — Business Decision Engine (FR-7) — Core Requirement
**Estimated time:** 4–5 days

### Tasks
- Write `retention_strategy.py`. For each customer, compute:
  - Churn probability (from the Phase 5 model)
  - Monthly revenue (already in the dataset)
  - CLV: `Monthly Charges × Expected Remaining Months` — document exactly how "Expected Remaining Months" is derived (e.g., a simple business assumption like "assume 12 months if still active, or a tenure-based heuristic" — the frozen spec deliberately leaves the exact formula flexible as long as it's documented and justified)
  - Revenue at risk: CLV × churn probability (or similar — document your formula)
  - Retention offer cost: fixed $20/customer (per frozen spec assumption)
  - Expected net benefit: (offer success rate × CLV) − offer cost, using the 25% success rate assumption
  - Recommended action: Retain / Monitor / No Action, based on expected net benefit thresholds you define and document
- **Threshold selection**: sweep candidate probability thresholds, calculate the resulting business value (net benefit) at each, and pick the one that maximizes it — this is your ROI-based threshold, replacing the default 0.5 from Phase 5.
- Go back and add a short addendum to Phase 5's evaluation write-up: state the chosen threshold and the resulting precision/recall/confusion matrix at that operating point, with a sentence on why it makes business sense (e.g., "we accept more false positives because a wasted $20 offer is cheap relative to a lost customer's CLV").

### Depends on
Phase 5 (needs trained model to generate probabilities). This is the phase that closes the loop opened in Phase 5.

### Deliverables
- `src/retention_strategy.py`
- Updated evaluation addendum (wherever Phase 5's writeup lives)
- A small output table/sample: e.g., top 20 highest-risk customers with their recommended action and expected net benefit, useful later for Dashboard Page 3

### Suggested commits
```
feat: implement CLV estimation
feat: implement retention offer cost-benefit calculation
feat: implement ROI-based threshold selection
feat: add retention action recommendation logic
docs: update model evaluation with chosen operating threshold
docs: document CLV and threshold assumptions and limitations
```

### Definition of Done
Given a customer's features, `retention_strategy.py` outputs a churn probability, CLV estimate, expected net benefit, and one of the three recommended actions — and you can explain, out loud, exactly why the threshold you picked is the right one for this business context (not just "it maximized F1").

### Pitfalls
- Don't let CLV become another rabbit hole. The frozen spec is explicit: the exact formula matters less than clearly explaining your choice and its limitations. Pick something simple, document it in two sentences, move on.
- Make sure the addendum to Phase 5 actually gets written — it's easy to do the threshold selection here and forget to close the loop back in the evaluation doc, which then reads inconsistently to anyone following your commit history.

---

## Phase 7 — Dashboard (FR-8)
**Estimated time:** 4–6 days

### Tasks
- Export final tables (cleaned data + model predictions + retention recommendations) from PostgreSQL/Python into a form Power BI can consume (direct Postgres connection, or a flat export — direct connection is more impressive if you're comfortable setting it up).
- Build **Page 1 (Executive Overview)**: KPI cards (Total Customers, Churn Rate, Monthly Revenue, Revenue at Risk, High-Risk Customers) + Revenue Breakdown, Churn Trend, Contract Distribution charts.
- Build **Page 2 (Customer Insights)**: the breakdown charts (contract, payment, internet service, gender, senior citizen, monthly charges, tenure) with interactive slicers.
- Build **Page 3 (Predictions & Recommendations)**: high-risk customer table, churn probability, recommended action, estimated financial impact — this is where Phase 6's output becomes visible to a stakeholder.
- Take clean screenshots of all three pages for the README.

### Depends on
Phase 6 (Page 3 needs the decision engine's output). Pages 1–2 could technically start as soon as Phase 3/4 data exists, but building all three together once everything's ready avoids redoing connections/formatting twice.

### Deliverables
- `dashboard/Customer_Churn.pbix`
- `reports/screenshots/` — page screenshots

### Suggested commits
```
feat: connect Power BI to PostgreSQL data source
feat: build executive overview dashboard page
feat: build customer insights dashboard page
feat: build predictions and recommendations dashboard page
docs: add dashboard screenshots to reports folder
```

### Definition of Done
All three pages render correctly, slicers work, and Page 3 correctly reflects the Phase 6 recommendations for at least a spot-checked sample of customers.

### Pitfalls
- Don't spend excessive time on visual polish before the numbers are verified — check a few customers' Page 3 values against your Python output directly, since a dashboard confidently displaying a wrong number is worse than a plain one displaying a right one.

---

## Phase 8 — Polish
**Estimated time:** 2–3 days

### Tasks
- Write the full `README.md`: project overview, architecture diagram (can reuse the one from the frozen spec), setup instructions, key business insights (pull from your Phase 3/4/6 findings — this is where your specific, non-generic finding should be front and center), assumptions and limitations, dashboard screenshots, future improvements.
- Clean up the repo: remove scratch files, make sure `requirements.txt` is accurate (`pip freeze` and prune), verify a fresh clone + setup actually works end-to-end.
- Write your resume bullet(s) based on what you actually built (not the aspirational version from early planning).
- Prepare answers to the Success Criteria questions from the frozen spec (Section 13) — actually write them out once, even briefly, so they're not being improvised for the first time in an interview.

### Depends on
All previous phases.

### Deliverables
- Final `README.md`
- Clean `requirements.txt`
- Resume bullet(s)
- Written interview prep notes (can be a personal doc, doesn't need to be in the repo)

### Suggested commits
```
docs: write comprehensive README with business insights
docs: add architecture diagram and dashboard screenshots
chore: clean up requirements.txt and repo structure
docs: add assumptions, limitations, and future improvements
```

### Definition of Done
A stranger could clone the repo, follow the README, and understand what the project does, why you made the decisions you made, and what you'd do differently with more time — without needing to ask you anything.

---

## Stretch Goals (only after Phase 8 / MVP is genuinely done)

| Goal | What it adds | Suggested commit prefix |
|---|---|---|
| SG-1: SHAP explainability | Global + per-customer "why did this model flag this customer" | `feat: add SHAP explainability` |
| SG-2: Retention campaign simulation | ROI comparison vs. random targeting — quantifies your model's value | `feat: add retention campaign simulation` |
| SG-3: Dashboard enhancements | What-if sliders, dynamic ROI scenarios | `feat: add dashboard what-if analysis` |

Do these in order — SG-2 (the simulation) is the one most likely to strengthen your interview story, so if you only have time for one, pick that.

---

## Rule going forward

Per the frozen spec: **improve based on findings from the data, not by adding new requirements.** If something comes up mid-build that feels like a "must add," write it down in a `future_improvements` note instead of adding it to this roadmap. This document doesn't get revised — it gets executed.
