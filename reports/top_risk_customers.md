# Phase 6 -- Top 20 Highest-Risk Active Customers

Scored with the XGBoost model at the ROI-optimal threshold (0.09). Only currently-active (not yet churned) customers are scored, since a retention offer only makes sense for someone who hasn't left.

**Recommended action breakdown (all 5174 active customers):** Retain: 3128, No Action: 1585, Monitor: 461

**Backtested business value on the held-out test set:** $57,091.65 at the optimal threshold, vs. $-6,246.60 at the default 0.5 threshold, vs. $-327,684.60 with no retention program at all.

| customer_id | churn_probability | monthly_charges | clv | revenue_at_risk | expected_net_benefit | recommended_action |
|---|---|---|---|---|---|---|
| 4912-PIGUY | 0.928 | $84.60 | $1015.20 | $942.15 | $215.54 | Retain |
| 0021-IKXGC | 0.925 | $72.10 | $865.20 | $800.18 | $180.04 | Retain |
| 1452-VOQCH | 0.919 | $75.10 | $901.20 | $828.53 | $187.13 | Retain |
| 4273-MBHYA | 0.918 | $89.35 | $1072.20 | $983.80 | $225.95 | Retain |
| 7577-SWIFR | 0.915 | $89.25 | $1071.00 | $980.25 | $225.06 | Retain |
| 7439-DKZTW | 0.915 | $80.55 | $966.60 | $884.36 | $201.09 | Retain |
| 1628-BIZYP | 0.914 | $85.00 | $1020.00 | $932.57 | $213.14 | Retain |
| 1941-HOSAM | 0.914 | $90.10 | $1081.20 | $988.16 | $227.04 | Retain |
| 2254-DLXRI | 0.914 | $79.15 | $949.80 | $867.85 | $196.96 | Retain |
| 3878-AVSOQ | 0.911 | $71.25 | $855.00 | $779.08 | $174.77 | Retain |
| 5542-TBBWB | 0.910 | $69.90 | $838.80 | $763.39 | $170.85 | Retain |
| 9603-OAIHC | 0.909 | $70.05 | $840.60 | $764.48 | $171.12 | Retain |
| 2018-QKYGT | 0.909 | $81.05 | $972.60 | $884.00 | $201.00 | Retain |
| 9605-WGJVW | 0.907 | $70.20 | $842.40 | $764.16 | $171.04 | Retain |
| 1640-PLFMP | 0.902 | $70.25 | $843.00 | $760.26 | $170.06 | Retain |
| 7465-ZZRVX | 0.901 | $70.35 | $844.20 | $760.51 | $170.13 | Retain |
| 5150-ITWWB | 0.895 | $94.85 | $1138.20 | $1018.62 | $234.65 | Retain |
| 8309-IEYJD | 0.894 | $70.60 | $847.20 | $757.31 | $169.33 | Retain |
| 4927-WWOOZ | 0.892 | $91.45 | $1097.40 | $978.80 | $224.70 | Retain |
| 8775-ERLNB | 0.890 | $74.30 | $891.60 | $793.48 | $178.37 | Retain |