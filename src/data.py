from __future__ import annotations

from pathlib import Path
import sqlite3
import pandas as pd

from .config import RAW_DIR, PROCESSED_DIR

RENAME = {
    # Current UCI/ucimlrepo feature names (X1-X23). UCI documents the
    # human-readable meanings separately in the variable descriptions.
    "X1": "credit_limit",
    "X2": "sex",
    "X3": "education",
    "X4": "marital_status",
    "X5": "age",
    "X6": "repay_sep",
    "X7": "repay_aug",
    "X8": "repay_jul",
    "X9": "repay_jun",
    "X10": "repay_may",
    "X11": "repay_apr",
    "X12": "bill_sep",
    "X13": "bill_aug",
    "X14": "bill_jul",
    "X15": "bill_jun",
    "X16": "bill_may",
    "X17": "bill_apr",
    "X18": "paid_sep",
    "X19": "paid_aug",
    "X20": "paid_jul",
    "X21": "paid_jun",
    "X22": "paid_may",
    "X23": "paid_apr",
    "ID": "customer_id",
    "LIMIT_BAL": "credit_limit",
    "SEX": "sex",
    "EDUCATION": "education",
    "MARRIAGE": "marital_status",
    "AGE": "age",
    "PAY_0": "repay_sep",
    "PAY_2": "repay_aug",
    "PAY_3": "repay_jul",
    "PAY_4": "repay_jun",
    "PAY_5": "repay_may",
    "PAY_6": "repay_apr",
    "BILL_AMT1": "bill_sep",
    "BILL_AMT2": "bill_aug",
    "BILL_AMT3": "bill_jul",
    "BILL_AMT4": "bill_jun",
    "BILL_AMT5": "bill_may",
    "BILL_AMT6": "bill_apr",
    "PAY_AMT1": "paid_sep",
    "PAY_AMT2": "paid_aug",
    "PAY_AMT3": "paid_jul",
    "PAY_AMT4": "paid_jun",
    "PAY_AMT5": "paid_may",
    "PAY_AMT6": "paid_apr",
    "default payment next month": "default_next_month",
    "default.payment.next.month": "default_next_month",
    "Y": "default_next_month",
}


def standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]

    # First use exact documented/current aliases.
    out = out.rename(columns=RENAME)

    # Then handle harmless case differences from local copies.
    lower_aliases = {str(k).lower(): v for k, v in RENAME.items()}
    case_map = {}
    for c in out.columns:
        key = str(c).strip().lower()
        if key in lower_aliases and c not in RENAME.values():
            case_map[c] = lower_aliases[key]
    if case_map:
        out = out.rename(columns=case_map)

    if "customer_id" not in out.columns:
        out.insert(0, "customer_id", range(1, len(out) + 1))
    return out


def fetch_data() -> pd.DataFrame:
    """Fetch official UCI dataset; fall back to a local CSV/XLS if present."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Local fallbacks first so the project can be re-run offline after first download.
    local_candidates = [
        RAW_DIR / "UCI_Credit_Card.csv",
        RAW_DIR / "default_of_credit_card_clients.csv",
        RAW_DIR / "default of credit card clients.xls",
        RAW_DIR / "default of credit card clients.xlsx",
    ]

    for path in local_candidates:
        if path.exists():
            if path.suffix.lower() == ".csv":
                df = pd.read_csv(path)
            else:
                # Original UCI XLS places variable names on row 2.
                df = pd.read_excel(path, header=1)
            df = standardise_columns(df)
            if "default_next_month" in df.columns:
                return df

    try:
        from ucimlrepo import fetch_ucirepo
        ds = fetch_ucirepo(id=350)
        df = pd.concat([ds.data.features.copy(), ds.data.targets.copy()], axis=1)
        df = standardise_columns(df)

        # Persist a local reusable copy using the project's standardized names.
        # This avoids reintroducing X1-X23 / legacy names on subsequent runs.
        raw_csv = RAW_DIR / "UCI_Credit_Card.csv"
        df.to_csv(raw_csv, index=False)
        return df
    except Exception as exc:
        raise RuntimeError(
            "Could not fetch the UCI dataset. Connect to the internet and rerun, or manually "
            "place UCI_Credit_Card.csv / the original XLS file inside data/raw/."
        ) from exc


def validate_and_clean(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return cleaned data plus a transparent data-quality log."""
    df = standardise_columns(df)

    required = [
        "customer_id", "credit_limit", "sex", "education", "marital_status", "age",
        "repay_sep", "repay_aug", "repay_jul", "repay_jun", "repay_may", "repay_apr",
        "bill_sep", "bill_aug", "bill_jul", "bill_jun", "bill_may", "bill_apr",
        "paid_sep", "paid_aug", "paid_jul", "paid_jun", "paid_may", "paid_apr",
        "default_next_month",
    ]
    missing_cols = sorted(set(required) - set(df.columns))
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    audit = []

    audit.append({
        "check": "raw_rows",
        "value": len(df),
        "action": "none"
    })
    audit.append({
        "check": "duplicate_customer_ids",
        "value": int(df["customer_id"].duplicated().sum()),
        "action": "drop duplicate IDs after first occurrence"
    })

    df = df.drop_duplicates(subset=["customer_id"], keep="first").copy()

    # Coerce expected fields to numeric.
    for c in required:
        if c != "customer_id":
            df[c] = pd.to_numeric(df[c], errors="coerce")

    audit.append({
        "check": "missing_values_after_numeric_coercion",
        "value": int(df[required].isna().sum().sum()),
        "action": "drop rows missing target/core identifiers; model pipeline imputes remaining predictors"
    })

    df = df.dropna(subset=["customer_id", "default_next_month", "credit_limit", "age"]).copy()

    # UCI documentation defines education 1–4 and marriage 1–3.
    # Widely circulated source copies contain small numbers of 0/5/6 and marriage 0.
    # Consolidate undocumented codes into the documented "other" category and log the action.
    bad_education = int((~df["education"].isin([1, 2, 3, 4])).sum())
    bad_marriage = int((~df["marital_status"].isin([1, 2, 3])).sum())

    audit.append({
        "check": "undocumented_education_codes",
        "value": bad_education,
        "action": "map values outside 1-4 to 4 (other)"
    })
    audit.append({
        "check": "undocumented_marital_codes",
        "value": bad_marriage,
        "action": "map values outside 1-3 to 3 (other)"
    })

    df.loc[~df["education"].isin([1, 2, 3, 4]), "education"] = 4
    df.loc[~df["marital_status"].isin([1, 2, 3]), "marital_status"] = 3

    if not set(df["default_next_month"].dropna().unique()).issubset({0, 1}):
        raise ValueError("Target is not binary after cleaning.")

    df["default_next_month"] = df["default_next_month"].astype(int)
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce").astype(int)

    # Hard plausibility checks; log rather than silently trimming economic outliers.
    audit.append({
        "check": "nonpositive_credit_limits",
        "value": int((df["credit_limit"] <= 0).sum()),
        "action": "retain but flag; expected to be zero in source"
    })
    audit.append({
        "check": "age_outside_18_100",
        "value": int(((df["age"] < 18) | (df["age"] > 100)).sum()),
        "action": "retain but flag; expected to be zero/negligible"
    })

    dq = pd.DataFrame(audit)
    return df.reset_index(drop=True), dq


def save_processed(df: pd.DataFrame) -> Path:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / "credit_risk_clean.csv"
    df.to_csv(path, index=False)
    return path


def build_sqlite(df: pd.DataFrame) -> Path:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / "credit_risk.db"
    with sqlite3.connect(path) as conn:
        df.to_sql("credit_accounts", conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_default ON credit_accounts(default_next_month)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_limit ON credit_accounts(credit_limit)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_age ON credit_accounts(age)")
    return path
