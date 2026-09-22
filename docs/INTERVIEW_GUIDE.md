# Interview Guide

## 30-second project explanation

“I built an end-to-end probability-of-default project using 30,000 credit-card accounts. I started with
SQL portfolio analysis and behavioural feature engineering, then benchmarked logistic regression against
non-linear challengers. Because credit risk needs meaningful probabilities, I evaluated calibration and
Brier score alongside ROC-AUC and PR-AUC. I then translated PDs into risk bands, a simple expected-loss
proxy and monitoring/governance outputs. I kept the test set untouched until final evaluation and documented
the fact that the dataset is historical Taiwan data, so I would not claim deployment validity.”

## Questions you should be able to answer

### Why not use accuracy?
Default is imbalanced. A model can achieve high accuracy by predicting the majority class while failing to
identify risky accounts.

### Why logistic regression?
It is an interpretable probability baseline and provides a strong reference point for whether added model
complexity is actually useful.

### Why Brier score?
It measures the quality of predicted probabilities, not only ranking. That matters when the output is a PD.

### What is calibration?
If a group of accounts receives 20% predicted PD, roughly 20% should default over the relevant horizon in a
well-calibrated setting.

### Why a separate validation and test set?
The validation set is used for model choice. The test set should estimate final out-of-sample performance,
so repeatedly using it for tuning would leak information into model development.

### What is wrong with the dataset?
It is from Taiwan in 2005 and omits many variables a real bank would use. It is useful for demonstrating the
workflow but not representative enough for current production lending.

### Why did you create repayment features?
Repeated delinquency, severity of delinquency, utilisation and payment behaviour capture economically
meaningful patterns rather than relying only on raw monthly fields.

### Is your expected-loss calculation Basel-compliant?
No. It is deliberately labelled a proxy: PD × assumed LGD × credit limit as an EAD approximation.

### What would you do next in a bank?
External validation, time-based validation, policy/legal review, richer bureau/income/product data,
independent model validation, monitoring thresholds and documented change control.
