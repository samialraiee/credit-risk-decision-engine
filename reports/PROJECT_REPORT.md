# Credit Risk Decision Engine — Project Report

## Executive summary

The analysis used **30,000 cleaned accounts** from 30,000 source rows. The observed next-month default rate was **22.12%**.

The validation-stage champion was **Hist Gradient Boosting**. On the held-out test set it achieved ROC-AUC **0.781**, PR-AUC **0.561**, Brier score **0.134** and KS **0.431**.

Under the project's explicitly illustrative false-negative / false-positive cost assumptions, the lowest-cost test threshold in the analysed grid was **0.150**. This is not presented as production credit policy.

## Model comparison

| model                  |   roc_auc |   pr_auc |   brier_score |   log_loss |     ks |   precision |   recall |     f1 |
|:-----------------------|----------:|---------:|--------------:|-----------:|-------:|------------:|---------:|-------:|
| hist_gradient_boosting |    0.7831 |   0.553  |        0.1342 |     0.4279 | 0.4349 |      0.6835 |   0.358  | 0.4698 |
| random_forest          |    0.7855 |   0.5567 |        0.1651 |     0.509  | 0.4321 |      0.5089 |   0.5787 | 0.5416 |
| logistic_regression    |    0.7702 |   0.5372 |        0.1829 |     0.556  | 0.4157 |      0.4626 |   0.6006 | 0.5226 |

## Risk-band performance

| risk_band   |   accounts |   observed_default_rate |
|:------------|-----------:|------------------------:|
| Low         |       1789 |                  0.0643 |
| Moderate    |       2189 |                  0.1544 |
| High        |       1074 |                  0.2737 |
| Very High   |        948 |                  0.6118 |

## Data-quality decisions

| check                                 |   value | action                                                                                 |
|:--------------------------------------|--------:|:---------------------------------------------------------------------------------------|
| raw_rows                              |   30000 | none                                                                                   |
| duplicate_customer_ids                |       0 | drop duplicate IDs after first occurrence                                              |
| missing_values_after_numeric_coercion |       0 | drop rows missing target/core identifiers; model pipeline imputes remaining predictors |
| undocumented_education_codes          |     345 | map values outside 1-4 to 4 (other)                                                    |
| undocumented_marital_codes            |      54 | map values outside 1-3 to 3 (other)                                                    |
| nonpositive_credit_limits             |       0 | retain but flag; expected to be zero in source                                         |
| age_outside_18_100                    |       0 | retain but flag; expected to be zero/negligible                                        |

## Interpretation

The model should be interpreted as a **risk-ranking and probability-estimation demonstration**, not as a deployable lending model. The most useful evidence is the combination of discrimination, calibration, portfolio segmentation and transparent governance rather than a single accuracy statistic.

## Limitations

- Data are from Taiwan and describe 2005 credit-card behaviour.
- The project does not incorporate current macroeconomic conditions, bureau history, income, collateral or product terms.
- The expected-loss calculation uses a simple LGD assumption and credit limit as an EAD proxy.
- Demographic fields require jurisdiction-specific legal/fair-lending review before real-world use.
- External validation on a current, representative population would be mandatory before deployment.
