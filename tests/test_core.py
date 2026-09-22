import pandas as pd
from src.data import validate_and_clean
from src.features import engineer_features
from src.evaluation import risk_band


def toy_df():
    return pd.DataFrame({
        "ID":[1,2],
        "LIMIT_BAL":[100000,200000],
        "SEX":[1,2],
        "EDUCATION":[1,5],
        "MARRIAGE":[2,0],
        "AGE":[30,40],
        "PAY_0":[0,2],"PAY_2":[0,2],"PAY_3":[0,0],"PAY_4":[0,0],"PAY_5":[0,0],"PAY_6":[0,0],
        "BILL_AMT1":[50000,100000],"BILL_AMT2":[45000,90000],"BILL_AMT3":[40000,80000],
        "BILL_AMT4":[35000,70000],"BILL_AMT5":[30000,60000],"BILL_AMT6":[25000,50000],
        "PAY_AMT1":[5000,1000],"PAY_AMT2":[5000,1000],"PAY_AMT3":[5000,1000],
        "PAY_AMT4":[5000,1000],"PAY_AMT5":[5000,1000],"PAY_AMT6":[5000,1000],
        "default.payment.next.month":[0,1]
    })


def test_clean_and_features():
    clean, dq = validate_and_clean(toy_df())
    assert len(clean) == 2
    assert clean.loc[1, "education"] == 4
    assert clean.loc[1, "marital_status"] == 3
    eng = engineer_features(clean)
    assert "avg_utilisation" in eng.columns
    assert eng.loc[1, "months_delinquent"] == 2


def test_risk_bands():
    assert risk_band(0.05) == "Low"
    assert risk_band(0.15) == "Moderate"
    assert risk_band(0.30) == "High"
    assert risk_band(0.50) == "Very High"
