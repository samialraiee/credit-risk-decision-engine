# Model Card

## Model purpose
Educational one-month default-probability estimation and portfolio-risk analysis.

## Intended users
Portfolio reviewers, recruiters and interviewers evaluating analytics capability.

## Prohibited use
Real lending or credit-limit decisions.

## Source population
Taiwan credit-card clients, 2005.

## Target
Default payment next month.

## Candidate models
- Logistic Regression
- Random Forest
- HistGradientBoosting

## Selection principle
Validation probability quality (Brier score) with ROC-AUC as a secondary criterion.

## Calibration
Champion is recalibrated using sigmoid calibration before held-out test evaluation.

## Key risks
- geographic/time representativeness;
- demographic-variable governance;
- omitted-variable bias;
- limited macro/product information;
- proxy expected-loss assumptions;
- absence of true production validation.

## Monitoring
- PD distribution;
- observed default rate;
- Brier score;
- ROC-AUC / PR-AUC;
- calibration;
- PSI for key numeric features;
- segment diagnostics.
