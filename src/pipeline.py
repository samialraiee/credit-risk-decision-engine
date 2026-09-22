from __future__ import annotations

from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd
import joblib

from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split

from .config import (
    RANDOM_STATE, TARGET, TABLES_DIR, FIGURES_DIR, MODELS_DIR, DASHBOARD_DIR,
    LGD_ASSUMPTION, FALSE_NEGATIVE_COST, FALSE_POSITIVE_COST
)
from .data import fetch_data, validate_and_clean, save_processed, build_sqlite
from .features import engineer_features, model_feature_lists
from .models import candidate_models, gradient_boosting_model
from .evaluation import metric_row, calibration_table, risk_band, threshold_economics
from .monitoring import drift_baseline, segment_diagnostics
from .reporting import create_figures, write_report


def ensure_dirs():
    for p in [TABLES_DIR, FIGURES_DIR, MODELS_DIR, DASHBOARD_DIR]:
        p.mkdir(parents=True, exist_ok=True)


def run_sql_reports(db_path):
    sql_path = Path(__file__).resolve().parents[1] / "sql" / "01_portfolio_analysis.sql"
    sql_text = sql_path.read_text(encoding="utf-8")
    statements = [s.strip() for s in sql_text.split("-- QUERY:") if s.strip()]

    with sqlite3.connect(db_path) as conn:
        for block in statements:
            header, *body = block.splitlines()
            name = header.strip().replace(" ", "_").lower()
            query = "\n".join(body).strip().rstrip(";")
            if not query:
                continue
            out = pd.read_sql_query(query, conn)
            out.to_csv(TABLES_DIR / f"sql_{name}.csv", index=False)


def main():
    ensure_dirs()

    raw = fetch_data()
    clean, dq = validate_and_clean(raw)
    save_processed(clean)
    db_path = build_sqlite(clean)
    run_sql_reports(db_path)

    df = engineer_features(clean)

    # Hold out test data before any model selection.
    train_val, test = train_test_split(
        df, test_size=0.20, stratify=df[TARGET], random_state=RANDOM_STATE
    )
    train, val = train_test_split(
        train_val, test_size=0.25, stratify=train_val[TARGET], random_state=RANDOM_STATE
    )
    # Final split proportions: 60% train, 20% validation, 20% test.

    numeric, categorical = model_feature_lists(include_demographics=True)
    features = numeric + categorical

    X_train, y_train = train[features], train[TARGET]
    X_val, y_val = val[features], val[TARGET]
    X_test, y_test = test[features], test[TARGET]

    models = candidate_models(include_demographics=True)
    models["hist_gradient_boosting"] = gradient_boosting_model(include_demographics=False)

    val_rows = []
    fitted = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        prob = model.predict_proba(X_val)[:, 1]
        row = {"model": name, **metric_row(y_val, prob)}
        val_rows.append(row)
        fitted[name] = model

    val_metrics = pd.DataFrame(val_rows)

    # PD modelling prioritises calibration. Select lowest Brier score;
    # ROC-AUC acts as tie-breaker if models are effectively tied.
    val_metrics["brier_rank"] = val_metrics["brier_score"].rank(method="min")
    val_metrics["auc_rank"] = val_metrics["roc_auc"].rank(ascending=False, method="min")
    val_metrics["selection_rank"] = val_metrics["brier_rank"] + 0.25 * val_metrics["auc_rank"]
    val_metrics = val_metrics.sort_values(["selection_rank", "brier_score", "roc_auc"], ascending=[True, True, False])

    champion_name = val_metrics.iloc[0]["model"]
    champion_base = fitted[champion_name]

    # Refit/calibrate using train+validation while preserving the test set.
    # Sigmoid calibration is stable and less prone to overfitting than isotonic on modest samples.
    X_train_val = train_val[features]
    y_train_val = train_val[TARGET]

    if champion_name == "hist_gradient_boosting":
        # Numeric-only challenger expects a compatible frame but can receive all columns;
        # its ColumnTransformer chooses the required numeric fields.
        pass

    calibrated = CalibratedClassifierCV(champion_base, method="sigmoid", cv=5)
    calibrated.fit(X_train_val, y_train_val)

    test_prob = calibrated.predict_proba(X_test)[:, 1]
    test_metrics = metric_row(y_test, test_prob)

    # Compare uncalibrated champion on test for calibration transparency.
    champion_refit = (
        gradient_boosting_model(include_demographics=False)
        if champion_name == "hist_gradient_boosting"
        else candidate_models(include_demographics=True)[champion_name]
    )
    champion_refit.fit(X_train_val, y_train_val)
    uncal_prob = champion_refit.predict_proba(X_test)[:, 1]
    uncal_test_metrics = metric_row(y_test, uncal_prob)

    cal = calibration_table(y_test, test_prob, bins=10)
    thresholds = threshold_economics(
        y_test, test_prob,
        fn_cost=FALSE_NEGATIVE_COST,
        fp_cost=FALSE_POSITIVE_COST,
    )
    best_threshold = float(
        thresholds.sort_values(["illustrative_cost", "threshold"]).iloc[0]["threshold"]
    )

    scored = test[[
        "customer_id", TARGET, "credit_limit", "age", "age_band",
        "credit_limit_band", "months_delinquent", "months_2plus_late",
        "avg_utilisation", "payment_to_bill_ratio"
    ]].copy()
    scored = scored.rename(columns={TARGET: "actual"})
    scored["probability_of_default"] = test_prob
    scored["risk_band"] = scored["probability_of_default"].map(risk_band)
    scored["flag_at_cost_threshold"] = (scored["probability_of_default"] >= best_threshold).astype(int)
    scored["ead_proxy"] = scored["credit_limit"].clip(lower=0)
    scored["lgd_assumption"] = LGD_ASSUMPTION
    scored["expected_loss_proxy"] = (
        scored["probability_of_default"] * scored["lgd_assumption"] * scored["ead_proxy"]
    )

    drift_cols = [
        "credit_limit", "age", "months_delinquent", "avg_utilisation",
        "payment_to_bill_ratio", "avg_bill", "avg_payment"
    ]
    drift = drift_baseline(train, test, drift_cols)
    segments = segment_diagnostics(scored)

    # Save core outputs.
    dq.to_csv(TABLES_DIR / "data_quality_log.csv", index=False)
    val_metrics.to_csv(TABLES_DIR / "model_comparison.csv", index=False)

    final_metrics = pd.DataFrame([
        {"model": f"{champion_name}_uncalibrated", **uncal_test_metrics},
        {"model": f"{champion_name}_sigmoid_calibrated", **test_metrics},
    ])
    final_metrics.to_csv(TABLES_DIR / "test_model_metrics.csv", index=False)

    cal.to_csv(TABLES_DIR / "calibration_table.csv", index=False)
    thresholds.to_csv(TABLES_DIR / "threshold_economics.csv", index=False)
    scored.to_csv(TABLES_DIR / "test_predictions.csv", index=False)
    drift.to_csv(TABLES_DIR / "drift_baseline.csv", index=False)
    segments.to_csv(TABLES_DIR / "segment_diagnostics.csv", index=False)

    # Dashboard-ready table.
    scored.to_csv(DASHBOARD_DIR / "credit_risk_dashboard.csv", index=False)

    # Model artifacts.
    joblib.dump(calibrated, MODELS_DIR / "champion_calibrated.joblib")
    joblib.dump({
        "champion": champion_name,
        "selected_threshold": best_threshold,
        "lgd_assumption": LGD_ASSUMPTION,
        "feature_columns": features,
    }, MODELS_DIR / "model_metadata.joblib")

    create_figures(scored, cal, val_metrics, thresholds)

    write_report(
        raw_rows=len(raw),
        clean_rows=len(clean),
        default_rate=clean[TARGET].mean(),
        model_comparison=val_metrics[[
            "model","roc_auc","pr_auc","brier_score","log_loss","ks","precision","recall","f1"
        ]],
        champion_name=champion_name,
        test_metrics=test_metrics,
        best_threshold=best_threshold,
        scored=scored,
        dq=dq,
    )

    print("\nPROJECT COMPLETE")
    print("=" * 60)
    print(f"Accounts analysed: {len(clean):,}")
    print(f"Observed default rate: {clean[TARGET].mean():.2%}")
    print(f"Champion: {champion_name}")
    print(f"Test ROC-AUC: {test_metrics['roc_auc']:.4f}")
    print(f"Test PR-AUC: {test_metrics['pr_auc']:.4f}")
    print(f"Test Brier score: {test_metrics['brier_score']:.4f}")
    print(f"Illustrative cost-optimal threshold: {best_threshold:.3f}")
    print("\nOpen reports/PROJECT_REPORT.md for the management summary.")


if __name__ == "__main__":
    main()
