from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss


def psi(expected, actual, bins=10):
    """Population Stability Index for a numeric variable."""
    expected = pd.Series(expected).dropna()
    actual = pd.Series(actual).dropna()
    if expected.empty or actual.empty:
        return np.nan

    cuts = np.unique(expected.quantile(np.linspace(0, 1, bins + 1)).values)
    if len(cuts) < 3:
        return np.nan

    cuts[0] = -np.inf
    cuts[-1] = np.inf

    e = pd.cut(expected, cuts, include_lowest=True).value_counts(normalize=True, sort=False)
    a = pd.cut(actual, cuts, include_lowest=True).value_counts(normalize=True, sort=False)

    e = e.clip(lower=1e-6)
    a = a.clip(lower=1e-6)
    return float(((a - e) * np.log(a / e)).sum())


def drift_baseline(train_df, test_df, columns):
    rows = []
    for c in columns:
        rows.append({"feature": c, "psi": psi(train_df[c], test_df[c])})
    return pd.DataFrame(rows).sort_values("psi", ascending=False)


def segment_diagnostics(df, y_col="actual", pd_col="probability_of_default"):
    frames = []
    for segment_col in ["age_band", "credit_limit_band"]:
        if segment_col not in df.columns:
            continue
        for segment, g in df.groupby(segment_col, observed=True):
            if len(g) < 30 or g[y_col].nunique() < 2:
                auc = np.nan
                ap = np.nan
            else:
                auc = roc_auc_score(g[y_col], g[pd_col])
                ap = average_precision_score(g[y_col], g[pd_col])
            frames.append({
                "segment_dimension": segment_col,
                "segment": str(segment),
                "accounts": len(g),
                "default_rate": g[y_col].mean(),
                "mean_pd": g[pd_col].mean(),
                "brier_score": brier_score_loss(g[y_col], g[pd_col]),
                "roc_auc": auc,
                "pr_auc": ap,
            })
    return pd.DataFrame(frames)
