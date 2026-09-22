# Power BI Build Guide

After running the project, import:

`dashboard/credit_risk_dashboard.csv`

## Page 1 — Executive portfolio risk

Cards:
- Accounts
- Observed default rate
- Average predicted PD
- Sum of expected-loss proxy
- High + Very High risk share

Charts:
- Accounts by risk band
- Observed default rate by risk band
- Expected-loss proxy by risk band
- Probability-of-default distribution
- Default rate by months delinquent

Slicers:
- Risk band
- Age band
- Credit-limit band

## Page 2 — Behavioural risk

Charts:
- Average utilisation by risk band
- Payment-to-bill ratio by risk band
- Months 2+ late vs observed default rate
- Credit limit vs PD scatter
- Accounts by credit-limit band

## Page 3 — Model governance

Import:
- `reports/tables/calibration_table.csv`
- `reports/tables/test_model_metrics.csv`
- `reports/tables/threshold_economics.csv`
- `reports/tables/drift_baseline.csv`

Show:
- ROC-AUC
- PR-AUC
- Brier score
- KS
- calibration chart
- threshold vs illustrative cost
- PSI by monitored feature

## Presentation rule
Make the dashboard read like a management risk report, not an ML demo.
Keep labels explicit and write “illustrative” wherever a policy or cost assumption is not empirical.
