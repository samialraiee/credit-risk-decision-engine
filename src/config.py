from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
REPORTS_DIR = ROOT / "reports"
TABLES_DIR = REPORTS_DIR / "tables"
FIGURES_DIR = REPORTS_DIR / "figures"
MODELS_DIR = ROOT / "models"
DASHBOARD_DIR = ROOT / "dashboard"

RANDOM_STATE = 42
TARGET = "default_next_month"

# Educational expected-loss assumption, clearly documented.
LGD_ASSUMPTION = 0.45

# Illustrative flagging economics:
# Missing a true defaulter is assumed to be more expensive than reviewing a non-defaulter.
FALSE_NEGATIVE_COST = 5.0
FALSE_POSITIVE_COST = 1.0
