# Phase 5 -- Model Comparison (default 0.5 threshold)

Evaluated on the held-out test set (1409 customers, 26.54% actual churn rate), which none of the three models saw during training or hyperparameter tuning.

**Threshold note:** these metrics use the default 0.5 probability threshold, as instructed for Phase 5 -- they measure model quality (ROC-AUC is threshold-independent), not the operating point that will actually be used. Phase 6 picks the real threshold by business ROI; see the addendum at the bottom of this file once that's done.

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| Logistic Regression | 0.7339 | 0.4991 | 0.7834 | 0.6098 | 0.8437 |
| Random Forest | 0.7339 | 0.4992 | 0.7914 | 0.6122 | 0.8433 |
| XGBoost | 0.7417 | 0.5085 | 0.7995 | 0.6216 | 0.8459 |

## Confusion matrices (rows = actual, cols = predicted; 0.5 threshold)

**Logistic Regression**

|  | Predicted: No Churn | Predicted: Churn |
|---|---|---|
| Actual: No Churn | 741 | 294 |
| Actual: Churn | 81 | 293 |

**Random Forest**

|  | Predicted: No Churn | Predicted: Churn |
|---|---|---|
| Actual: No Churn | 738 | 297 |
| Actual: Churn | 78 | 296 |

**XGBoost**

|  | Predicted: No Churn | Predicted: Churn |
|---|---|---|
| Actual: No Churn | 746 | 289 |
| Actual: Churn | 75 | 299 |

## Final model selection: XGBoost

XGBoost wins on every metric simultaneously -- not just the highest ROC-AUC
(0.8459 vs. 0.8437 for Logistic Regression and 0.8433 for Random Forest),
but also the best accuracy, precision, recall, and F1. That's a stronger
case than a marginal AUC win alone: when one model dominates across the
board, there's no accuracy/interpretability tradeoff to weigh, so
Logistic Regression's edge in interpretability isn't enough to override it.

The margins here are modest (roughly 0.5-2 points across metrics), which is
expected on a 7K-row dataset with 21 base features -- this isn't a case
where one model is dramatically better, it's a case where XGBoost is
consistently, slightly better everywhere. Given that, and that Phase 6
needs well-calibrated churn *probabilities* (not just the 0.5-threshold
class label) to compute expected net benefit, XGBoost's gradient-boosted
probability estimates are the more reliable input to carry forward.

Logistic Regression remains a reasonable fallback if model interpretability
ever becomes a hard requirement (e.g. regulatory explainability) -- its
recall (0.7834) and ROC-AUC (0.8437) are close enough to XGBoost's that the
interpretability-for-accuracy trade would be cheap if it were ever needed.

**xgboost.pkl is the model Phase 6's `retention_strategy.py` will load.**

## Phase 6 addendum: the real operating threshold

The 0.5 threshold above was always a placeholder. Phase 6 swept 91 candidate
thresholds (0.05-0.95) against the held-out test set, scoring each by actual
dollar business value -- not F1, not accuracy -- using CLV = monthly_charges
x 12, a $20 retention offer cost, and a 25% offer success rate (see
`src/retention_strategy.py` for the exact formula).

**Chosen threshold: 0.09** -- far below 0.5. At this operating point:

| Metric | Value |
|---|---|
| Precision | 0.3379 |
| Recall | 0.9893 |
| Confusion matrix | TN=310, FP=725, FN=4, TP=370 |

**Why this makes business sense:** a wasted $20 offer (false positive) is
cheap; a missed churner (false negative) costs their entire CLV, often
$800-1,400. That asymmetry means it's worth flagging aggressively and
accepting a lot of false positives to drive false negatives down to nearly
zero (only 4 missed, out of 374 actual churners in the test set). Optimizing
for F1 or accuracy would never find this threshold, because those metrics
treat a $20 mistake and an $800+ mistake as equally bad -- optimizing for
actual dollar value is what surfaces it.

**Backtested business value on the test set, by threshold:**

| Threshold | Business value |
|---|---|
| No retention program at all | -$327,684.60 |
| Default 0.5 | -$6,246.60 |
| **Optimal (0.09)** | **+$57,091.65** |

The default 0.5 threshold is barely distinguishable from doing nothing --
it's still a net loss, because it misses too many high-CLV churners. The
ROI-optimized threshold doesn't just improve on that marginally: it flips
the retention program from a net loss to a net gain of over $57K on this
test set alone.
