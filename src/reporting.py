from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .config import FIGURES_DIR, REPORTS_DIR, TABLES_DIR


def _savefig(name):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / name, dpi=160, bbox_inches="tight")
    plt.close()


def create_figures(scored, calibration, model_comparison, threshold_table):
    # Risk band distribution
    scored["risk_band"].value_counts().reindex(
        ["Low", "Moderate", "High", "Very High"]
    ).plot(kind="bar", title="Accounts by Risk Band")
    plt.ylabel("Accounts")
    _savefig("01_risk_band_distribution.png")

    # Default rate by risk band
    (
        scored.groupby("risk_band", observed=True)["actual"].mean()
        .reindex(["Low", "Moderate", "High", "Very High"])
        .plot(kind="bar", title="Observed Default Rate by Risk Band")
    )
    plt.ylabel("Observed default rate")
    _savefig("02_default_rate_by_risk_band.png")

    # Calibration
    plt.plot(calibration["predicted_pd"], calibration["observed_default_rate"], marker="o")
    plt.plot([0,1], [0,1], linestyle="--")
    plt.xlabel("Mean predicted PD")
    plt.ylabel("Observed default rate")
    plt.title("Probability Calibration")
    _savefig("03_calibration.png")

    # Model comparison
    mc = model_comparison.set_index("model")[["roc_auc", "pr_auc"]]
    mc.plot(kind="bar", title="Validation Model Comparison")
    plt.ylabel("Score")
    _savefig("04_model_comparison.png")

    # Threshold economics
    plt.plot(threshold_table["threshold"], threshold_table["illustrative_cost"], marker="o")
    plt.xlabel("Flagging threshold")
    plt.ylabel("Illustrative cost units")
    plt.title("Threshold Economics")
    _savefig("05_threshold_economics.png")


def write_report(
    raw_rows,
    clean_rows,
    default_rate,
    model_comparison,
    champion_name,
    test_metrics,
    best_threshold,
    scored,
    dq,
):
    top_band = (
        scored.groupby("risk_band", observed=True)["actual"]
        .agg(["count", "mean"])
        .reindex(["Low", "Moderate", "High", "Very High"])
    )

    lines = []
    lines.append("# Credit Risk Decision Engine — Project Report\n")
    lines.append("## Executive summary\n")
    lines.append(
        f"The analysis used **{clean_rows:,} cleaned accounts** from {raw_rows:,} source rows. "
        f"The observed next-month default rate was **{default_rate:.2%}**.\n"
    )
    lines.append(
        f"The validation-stage champion was **{champion_name.replace('_',' ').title()}**. "
        f"On the held-out test set it achieved ROC-AUC **{test_metrics['roc_auc']:.3f}**, "
        f"PR-AUC **{test_metrics['pr_auc']:.3f}**, Brier score **{test_metrics['brier_score']:.3f}** "
        f"and KS **{test_metrics['ks']:.3f}**.\n"
    )
    lines.append(
        f"Under the project's explicitly illustrative false-negative / false-positive cost assumptions, "
        f"the lowest-cost test threshold in the analysed grid was **{best_threshold:.3f}**. "
        "This is not presented as production credit policy.\n"
    )

    lines.append("## Model comparison\n")
    lines.append(model_comparison.round(4).to_markdown(index=False) + "\n")

    lines.append("## Risk-band performance\n")
    lines.append(top_band.rename(columns={"count":"accounts","mean":"observed_default_rate"}).round(4).to_markdown() + "\n")

    lines.append("## Data-quality decisions\n")
    lines.append(dq.to_markdown(index=False) + "\n")

    lines.append("## Interpretation\n")
    lines.append(
        "The model should be interpreted as a **risk-ranking and probability-estimation demonstration**, "
        "not as a deployable lending model. The most useful evidence is the combination of discrimination, "
        "calibration, portfolio segmentation and transparent governance rather than a single accuracy statistic.\n"
    )

    lines.append("## Limitations\n")
    lines.append(
        "- Data are from Taiwan and describe 2005 credit-card behaviour.\n"
        "- The project does not incorporate current macroeconomic conditions, bureau history, income, collateral or product terms.\n"
        "- The expected-loss calculation uses a simple LGD assumption and credit limit as an EAD proxy.\n"
        "- Demographic fields require jurisdiction-specific legal/fair-lending review before real-world use.\n"
        "- External validation on a current, representative population would be mandatory before deployment.\n"
    )

    (REPORTS_DIR / "PROJECT_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
