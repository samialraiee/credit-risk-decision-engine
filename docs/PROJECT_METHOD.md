# Project Method

## 1. Problem formulation
Estimate one-month probability of default and translate it into an auditable portfolio-risk view.

## 2. Data split
The project holds out 20% of accounts as the final test set before model selection.

Remaining data:
- 60% training
- 20% validation
- 20% test

All splits are stratified on default.

## 3. Model selection
Candidate models are fitted only on training data and compared on validation data.

The selection rule prioritises **Brier score** because this is a probability-of-default project.
ROC-AUC acts as a secondary ranking measure rather than the sole objective.

## 4. Calibration
After champion selection, the champion is calibrated with sigmoid calibration using cross-validation
over the combined train+validation sample. The final test set remains untouched until final evaluation.

## 5. Threshold economics
Classification thresholds are not model parameters. The project therefore analyses a grid of thresholds
using explicit illustrative false-negative and false-positive costs rather than assuming 0.50 is automatically optimal.

## 6. Governance
The project stores:
- data-quality audit;
- model comparison;
- calibration;
- threshold economics;
- drift baseline;
- segment diagnostics;
- model metadata;
- documented limitations.
