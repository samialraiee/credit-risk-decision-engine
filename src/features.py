from __future__ import annotations

import numpy as np
import pandas as pd

REPAY = ["repay_sep", "repay_aug", "repay_jul", "repay_jun", "repay_may", "repay_apr"]
BILLS = ["bill_sep", "bill_aug", "bill_jul", "bill_jun", "bill_may", "bill_apr"]
PAID = ["paid_sep", "paid_aug", "paid_jul", "paid_jun", "paid_may", "paid_apr"]


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()

    x["avg_bill"] = x[BILLS].mean(axis=1)
    x["max_bill"] = x[BILLS].max(axis=1)
    x["bill_volatility"] = x[BILLS].std(axis=1)

    x["avg_payment"] = x[PAID].mean(axis=1)
    x["total_payment_6m"] = x[PAID].sum(axis=1)
    x["payment_volatility"] = x[PAID].std(axis=1)

    x["months_delinquent"] = (x[REPAY] > 0).sum(axis=1)
    x["months_2plus_late"] = (x[REPAY] >= 2).sum(axis=1)
    x["max_delinquency"] = x[REPAY].max(axis=1)
    x["recent_delinquency"] = (x["repay_sep"] > 0).astype(int)

    safe_limit = x["credit_limit"].replace(0, np.nan)
    utilisation = x[BILLS].clip(lower=0).div(safe_limit, axis=0)
    x["avg_utilisation"] = utilisation.mean(axis=1)
    x["max_utilisation"] = utilisation.max(axis=1)

    positive_bills = x[BILLS].clip(lower=0).sum(axis=1)
    x["payment_to_bill_ratio"] = (
        x["total_payment_6m"] / positive_bills.replace(0, np.nan)
    ).replace([np.inf, -np.inf], np.nan).fillna(0)

    x["recent_bill_change"] = x["bill_sep"] - x["bill_aug"]
    x["recent_payment_change"] = x["paid_sep"] - x["paid_aug"]

    x["age_band"] = pd.cut(
        x["age"],
        bins=[0, 29, 39, 49, 59, np.inf],
        labels=["<30", "30-39", "40-49", "50-59", "60+"],
        include_lowest=True,
    )

    x["credit_limit_band"] = pd.cut(
        x["credit_limit"],
        bins=[-np.inf, 50000, 100000, 200000, 500000, np.inf],
        labels=["<50k", "50k-99k", "100k-199k", "200k-499k", "500k+"],
        right=False,
    )

    return x


def model_feature_lists(include_demographics: bool = True):
    numeric = [
        "credit_limit", "age",
        *REPAY, *BILLS, *PAID,
        "avg_bill", "max_bill", "bill_volatility",
        "avg_payment", "total_payment_6m", "payment_volatility",
        "months_delinquent", "months_2plus_late", "max_delinquency",
        "recent_delinquency", "avg_utilisation", "max_utilisation",
        "payment_to_bill_ratio", "recent_bill_change", "recent_payment_change",
    ]

    categorical = []
    if include_demographics:
        categorical = ["sex", "education", "marital_status"]

    return numeric, categorical
