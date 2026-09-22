from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


def ks_statistic(y_true, prob):
    fpr, tpr, _ = roc_curve(y_true, prob)
    return float(np.max(tpr - fpr))


def metric_row(y_true, prob, threshold=0.5):
    prob = np.asarray(prob)
    y_true = np.asarray(y_true)
    pred = (prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0,1]).ravel()

    return {
        "roc_auc": roc_auc_score(y_true, prob),
        "pr_auc": average_precision_score(y_true, prob),
        "brier_score": brier_score_loss(y_true, prob),
        "log_loss": log_loss(y_true, np.c_[1-prob, prob], labels=[0,1]),
        "ks": ks_statistic(y_true, prob),
        "precision": precision_score(y_true, pred, zero_division=0),
        "recall": recall_score(y_true, pred, zero_division=0),
        "f1": f1_score(y_true, pred, zero_division=0),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        "threshold": threshold,
    }


def calibration_table(y_true, prob, bins=10):
    t = pd.DataFrame({"actual": np.asarray(y_true), "pd": np.asarray(prob)})
    t["bucket"] = pd.qcut(t["pd"], q=bins, duplicates="drop")
    out = (
        t.groupby("bucket", observed=True)
        .agg(
            accounts=("actual", "size"),
            predicted_pd=("pd", "mean"),
            observed_default_rate=("actual", "mean"),
            min_pd=("pd", "min"),
            max_pd=("pd", "max"),
        )
        .reset_index()
    )
    out["calibration_gap"] = out["predicted_pd"] - out["observed_default_rate"]
    return out


def risk_band(prob):
    if prob < 0.10:
        return "Low"
    if prob < 0.20:
        return "Moderate"
    if prob < 0.40:
        return "High"
    return "Very High"


def threshold_economics(y_true, prob, fn_cost=5.0, fp_cost=1.0):
    rows = []
    for threshold in np.arange(0.05, 0.81, 0.025):
        pred = (np.asarray(prob) >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0,1]).ravel()
        total_cost = fn_cost * fn + fp_cost * fp
        rows.append({
            "threshold": round(float(threshold), 3),
            "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
            "illustrative_cost": float(total_cost),
            "flag_rate": float(pred.mean()),
            "recall": float(tp / (tp + fn)) if tp + fn else 0.0,
            "precision": float(tp / (tp + fp)) if tp + fp else 0.0,
        })
    return pd.DataFrame(rows)
