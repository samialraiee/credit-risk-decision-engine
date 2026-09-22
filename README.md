# Credit Risk Decision Engine & Model Governance

**Portfolio focus:** Financial Risk Analytics · SQL · Python · Machine Learning · Model Governance

## Executive summary

This project builds an end-to-end probability-of-default (PD) workflow for a credit-card portfolio.
It is intentionally designed as a **risk analytics project**, not a leaderboard-style machine-learning
exercise.

The pipeline:

1. retrieves and validates the UCI *Default of Credit Card Clients* dataset;
2. creates an analytics-ready SQLite database;
3. performs SQL-based portfolio analysis;
4. engineers behavioural credit-risk features;
5. separates train / validation / test data;
6. compares an interpretable logistic-regression baseline with non-linear challenger models;
7. evaluates discrimination **and** probability calibration;
8. calibrates the strongest challenger where appropriate;
9. creates risk bands and an illustrative expected-loss view;
10. generates model-governance diagnostics, drift baselines and dashboard-ready files;
11. writes a reproducible management-style analysis report.

## Results at a glance

The completed analysis covers **30,000 accounts** with an observed default rate of **22.12%**.
The reported champion is **HistGradientBoosting**, with:

| Metric | Result |
|:--|--:|
| ROC-AUC | 0.7812 |
| PR-AUC | 0.5607 |
| Brier score | 0.1345 |
| Illustrative cost-optimal threshold | 0.150 |

The threshold is an analytical illustration under explicit cost assumptions, not a production credit
policy. Detailed governance notes and limitations are in `reports/MODEL_CARD.md` and
`reports/PROJECT_REPORT.md`.

## Business question

> Which customers appear most likely to default next month, what behavioural signals drive that risk,
> how reliable are the predicted probabilities, and how should model output be translated into
> an interpretable risk-management view?

The project focuses on **probability of default**, because a calibrated PD is more useful for risk
management than a simple 0/1 prediction.

## Data

Primary source: **UCI Machine Learning Repository — Default of Credit Card Clients**

- 30,000 observations
- 23 predictive variables
- target: default payment next month
- borrower characteristics, credit limits, six months of repayment status, bill statements and payments
- Taiwan, 2005
- CC BY 4.0

Dataset citation:

> Yeh, I. (2009). Default of Credit Card Clients [Dataset]. UCI Machine Learning Repository.
> https://doi.org/10.24432/C55S3H

### Important limitation

The data are historical and geographically specific. This project **does not claim** that the resulting
model is suitable for current UK or US lending decisions. Its purpose is to demonstrate analytical
discipline: data quality, SQL, feature engineering, probability modelling, calibration, explainability,
threshold economics, monitoring and governance.

## Repository structure

```text
jpm_credit_risk_project/
├── data/
│   ├── raw/
│   └── processed/
├── dashboard/
│   └── POWER_BI_GUIDE.md
├── docs/
│   ├── DATA_DICTIONARY.md
│   ├── INTERVIEW_GUIDE.md
│   └── PROJECT_METHOD.md
├── models/
├── notebooks/
│   └── 01_credit_risk_walkthrough.ipynb
├── reports/
│   ├── figures/
│   ├── tables/
│   ├── MODEL_CARD.md
│   └── PROJECT_REPORT.md
├── sql/
│   ├── 01_portfolio_analysis.sql
│   └── 02_monitoring_queries.sql
├── src/
│   ├── config.py
│   ├── data.py
│   ├── features.py
│   ├── models.py
│   ├── evaluation.py
│   ├── monitoring.py
│   ├── reporting.py
│   └── pipeline.py
├── tests/
├── RUN_PROJECT.bat
├── RUN_PROJECT.ps1
├── requirements.txt
└── README.md
```

## One-click Windows run

Extract the ZIP and double-click:

`RUN_PROJECT.bat`

It will:

- create a virtual environment;
- install dependencies;
- fetch the UCI dataset;
- run the complete pipeline;
- write final outputs into `reports/`, `models/`, `data/processed/` and `dashboard/`.

If Windows blocks the batch file, open PowerShell in the project folder and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\RUN_PROJECT.ps1
```

## Core modelling design

### 1. Interpretable baseline
**Logistic Regression**

Why:
- transparent benchmark;
- produces probabilities;
- lets us test whether non-linear complexity materially improves risk ranking/calibration.

### 2. Challenger models
**Random Forest** and **HistGradientBoosting**

Why:
- capture non-linearities and interactions;
- contrast with the linear baseline;
- remain reproducible using scikit-learn.

### Champion model

HistGradientBoosting is the selected champion for the completed analysis. It is compared with logistic
regression and random forest using both ranking metrics and probability-quality metrics. The selection
process uses validation data, with the held-out test set reserved for final reporting.

### 3. Probability calibration
A probability-of-default model should be evaluated on more than ranking. The project reports:

- ROC-AUC
- PR-AUC
- Brier score
- log loss
- precision
- recall
- F1
- KS statistic
- calibration curve / calibration table
- confusion matrix at an illustrative threshold

The validation set selects the candidate; the held-out test set is used once for final reporting.

## Feature engineering

The project creates behavioural features including:

- average / maximum utilisation
- six-month total and average payments
- payment-to-bill ratio
- number of delinquent months
- number of 2+ month delinquencies
- maximum delinquency
- recent bill change
- recent payment change
- bill volatility
- payment volatility

No post-outcome information is used.

## Expected-loss illustration

For portfolio interpretation the project creates a **demonstration expected-loss proxy**:

`EL_proxy = PD × LGD_assumption × EAD_proxy`

where:
- PD = model probability of default;
- LGD is an explicit configurable assumption (default 45%);
- EAD proxy uses current credit limit.

This is an educational approximation — not Basel-compliant production ECL.

## Governance

The project deliberately documents:

- source-data issues;
- target definition;
- leakage controls;
- train/validation/test design;
- calibration;
- model selection rule;
- demographic-variable treatment;
- segment diagnostics;
- drift baselines;
- threshold assumptions;
- limitations and intended use.

## Monitoring and drift diagnostics

The project creates monitoring baselines for predicted-PD distributions, observed default rates,
calibration, discrimination, segment performance and population stability for key numeric features.
The SQL monitoring queries are in `sql/02_monitoring_queries.sql`, and the implementation is in
`src/monitoring.py`. These diagnostics are intended to support model review; they are not a substitute
for ongoing production monitoring, independent validation or governance approval.

## Generated outputs

After a successful local run, the most important generated files are:

- `reports/PROJECT_REPORT.md`
- `reports/MODEL_CARD.md`
- `reports/tables/model_comparison.csv`
- `reports/tables/test_predictions.csv`
- `reports/tables/calibration_table.csv`
- `reports/tables/threshold_economics.csv`
- `reports/tables/segment_diagnostics.csv`
- `reports/figures/`
- `dashboard/credit_risk_dashboard.csv`
- `data/processed/credit_risk.db`

Generated datasets, database files, model binaries, dashboard extracts, tables and figures are
intentionally ignored by Git. The repository contains the code, SQL, documentation and report
templates needed to recreate them.

## CV wording

> **Credit Risk Decision Engine & Model Governance — Python, SQL, Machine Learning**  
> Built an end-to-end PD pipeline on 30,000 credit-card accounts, combining SQL portfolio analysis,
> behavioural feature engineering and calibrated machine-learning models. Benchmarked interpretable
> logistic regression against non-linear challengers using ROC-AUC, PR-AUC, Brier score and calibration;
> translated model output into risk bands, expected-loss proxies and governance/monitoring diagnostics.

## Ethics / responsible use

This repository is educational. Real credit decisions require jurisdiction-specific legal review,
fair-lending controls, robust model-risk governance, independent validation and current representative data.
